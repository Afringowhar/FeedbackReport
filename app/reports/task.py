from celery import shared_task
from .models import ReportTask, HTMLReport, PDFReport
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime
import logging
from django.utils import timezone
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage



logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def generate_html_report(self, task_id, student_id, events):
    try:
        task = ReportTask.objects.get(task_id=task_id)
        task.status = 'processing'
        task.started_at = timezone.now()
        task.save()
        
        # Process and sort events
        sorted_events = sorted(events, key=lambda x: x['unit'])
        question_aliases = [f"Q{i+1}" for i in range(len(sorted_events))]
        
        # Calculate submission count
        submission_count = sum(1 for event in sorted_events if event.get('type') == 'submission')
        
        # Create zipped data for template
        zipped_events = list(zip(sorted_events, question_aliases))
        
        context = {
            'student_id': student_id,
            'zipped_events': zipped_events,
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_events': len(sorted_events),
            'submission_count': submission_count,
        }
        
        html_content = render_to_string('reports/student_report.html', context)
        
        HTMLReport.objects.create(
            task=task,
            content=html_content,
            student_id=student_id
        )
        
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        return True

    except Exception as e:
        task = ReportTask.objects.get(task_id=task_id)
        task.status = 'failed'
        task.save()
        logger.error(f"Report generation failed: {str(e)}")
        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=5)
def generate_pdf_report(self, task_id, student_id, html_task_id):
    try:
        # Get and update task status
        task = ReportTask.objects.get(task_id=task_id)
        task.status = 'processing'
        task.started_at = timezone.now()
        task.save()
        
        # Verify HTML report is ready
        html_task = ReportTask.objects.get(task_id=html_task_id)
        if html_task.status != 'completed':
            raise Exception("HTML report not ready yet")
            
        html_report = HTMLReport.objects.get(task=html_task)
        
        # Create PDF with improved formatting
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        
        # Set up styles
        pdf.setTitle(f"Student Report - {student_id}")
        
        # Header
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(72, 750, "Student Performance Report")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(72, 730, f"Student ID: {student_id}")
        pdf.drawString(72, 715, f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Draw a line separator
        pdf.line(72, 710, 540, 710)
        
        # Summary section
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(72, 690, "Summary")
        pdf.setFont("Helvetica", 12)
        
        # Parse HTML to get counts
        soup = BeautifulSoup(html_report.content, 'html.parser')
        total_events = len(soup.select('table tbody tr'))
        total_submissions = len(soup.select('table tbody tr.submission-row'))
        
        pdf.drawString(72, 670, f"Total Events: {total_events}")
        pdf.drawString(72, 655, f"Total Submissions: {total_submissions}")
        
        # Event Timeline section
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(72, 635, "Event Timeline")
        
        # Table headers
        pdf.setFont("Helvetica-Bold", 12)
        y_position = 615
        pdf.drawString(72, y_position, "Question")
        pdf.drawString(150, y_position, "Unit")
        pdf.drawString(200, y_position, "Type")
        pdf.drawString(300, y_position, "Timestamp")
        
        # Draw line under headers
        y_position -= 5
        pdf.line(72, y_position, 540, y_position)
        y_position -= 15
        
        # Process events data
        pdf.setFont("Helvetica", 10)
        
        rows = soup.select('table tbody tr')
        
        for row in rows:
            if y_position < 100:  # Near bottom of page
                pdf.showPage()
                y_position = 750
                # Redraw headers on new page
                pdf.setFont("Helvetica-Bold", 12)
                pdf.drawString(72, y_position, "Question")
                pdf.drawString(150, y_position, "Unit")
                pdf.drawString(200, y_position, "Type")
                pdf.drawString(300, y_position, "Timestamp")
                y_position -= 5
                pdf.line(72, y_position, 540, y_position)
                y_position -= 15
                pdf.setFont("Helvetica", 10)
            
            cells = row.find_all('td')
            if len(cells) == 4:
                # Highlight submissions
                if 'submission-row' in row.get('class', []):
                    pdf.setFillColorRGB(0.9, 0.98, 0.95)
                    pdf.rect(70, y_position-10, 470, 15, fill=True, stroke=False)
                    pdf.setFillColorRGB(0, 0, 0)
                
                pdf.drawString(72, y_position, cells[0].get_text())
                pdf.drawString(150, y_position, cells[1].get_text())
                pdf.drawString(200, y_position, cells[2].get_text())
                pdf.drawString(300, y_position, cells[3].get_text())
                y_position -= 20
        
        # Footer
        pdf.setFont("Helvetica", 8)
        pdf.drawString(72, 30, "Report generated with ❤ by Meow")
        
        pdf.save()
        
        # # Create PDF record
        # PDFReport.objects.create(
        #     task=task,
        #     file_data=buffer.getvalue(),
        #     student_id=student_id
        # )

        #  Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/pdf/{student_id}_{timestamp}.pdf"
        
        # Save to storage
        file_path = default_storage.save(filename, ContentFile(buffer.getvalue()))
        
        # Create PDF record
        PDFReport.objects.create(
            task=task,
            file_data=buffer.getvalue(),
            file_path=file_path,
            student_id=student_id
        )
        
        
        # Update task status
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        logger.info(f"Successfully generated PDF report for student {student_id}")
        return True

    except Exception as e:
        # Handle failure
        task = ReportTask.objects.get(task_id=task_id)
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        
        logger.error(f"PDF generation failed for task {task_id}: {str(e)}", exc_info=True)
        raise self.retry(exc=e, countdown=60)  # Retry after 1 minute



