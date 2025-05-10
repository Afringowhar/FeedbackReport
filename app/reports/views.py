from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from .models import ReportTask, HTMLReport, PDFReport
from .task import generate_html_report, generate_pdf_report
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .llm_integration import generate_insights
import os
import uuid
import json
import io


class GenerateHTMLReportView(APIView):
    """
    API view to generate only HTML reports.
    
    Accepts both direct JSON payload and file uploads.
    Returns task ID for HTML report.
    """
    parser_classes = (MultiPartParser, JSONParser)
    
    def post(self, request):
        try:
            # Extract the data from either JSON payload or uploaded file
            data = self._extract_data(request)
            if isinstance(data, Response):  # Error case
                return data
            
            result = {}
            
            # Generate reports for each student in the data
            if isinstance(data, list):
                # Batch processing
                task_ids = []
                for student_data in data:
                    student_result = self._generate_html_report_for_student(student_data)
                    task_ids.append(student_result)
                
                result['batch_task_ids'] = task_ids
                result['batch_status'] = f'Processing batch of {len(data)} students'
            else:
                # Single student processing
                student_result = self._generate_html_report_for_student(data)
                result.update(student_result)
            
            return Response(result, status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_html_report_for_student(self, student_data):
        """Generate HTML report for a single student."""
        html_task_id = str(uuid.uuid4())
        ReportTask.objects.create(task_id=html_task_id)
        
        generate_html_report.delay(
            html_task_id,
            student_data['student_id'],
            student_data['events']
        )
        
        return {'html_task_id': html_task_id}
    
    def _extract_data(self, request):
        """Extract and validate data from request, handling both file uploads and direct JSON."""
        # Same implementation as in GenerateReportView
        if 'file' in request.FILES:
            file = request.FILES['file']
            if not file.name.endswith('.json'):
                return Response(
                    {"error": "Only JSON files are allowed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                path = default_storage.save(f'tmp/{file.name}', ContentFile(file.read()))
                with default_storage.open(path) as f:
                    data = json.load(f)
                default_storage.delete(path)
                
                if isinstance(data, list):
                    for student in data:
                        if not all(key in student for key in ['student_id', 'events', 'namespace']):
                            return Response(
                                {"error": "Invalid student data format. Required fields: namespace, student_id, events"},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    return data
                
                if not all(key in data for key in ['student_id', 'events', 'namespace']):
                    return Response(
                        {"error": "Invalid payload format. Required fields: namespace, student_id, events"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return data
                
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid JSON file"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        data = request.data
        
        if isinstance(data, list):
            for student in data:
                if not all(key in student for key in ['student_id', 'events', 'namespace']):
                    return Response(
                        {"error": "Invalid student data format. Required fields: namespace, student_id, events"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return data
        
        if not all(key in data for key in ['student_id', 'events', 'namespace']):
            return Response(
                {"error": "Invalid payload format. Required fields: namespace, student_id, events"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return data


class GeneratePDFReportView(APIView):
    """
    API view to generate only PDF reports.
    
    Accepts both direct JSON payload and file uploads.
    Returns task ID for PDF report.
    """
    parser_classes = (MultiPartParser, JSONParser)
    
    def post(self, request):
        try:
            # Extract the data from either JSON payload or uploaded file
            data = self._extract_data(request)
            if isinstance(data, Response):  # Error case
                return data
            
            result = {}
            
            # Generate reports for each student in the data
            if isinstance(data, list):
                # Batch processing
                task_ids = []
                for student_data in data:
                    student_result = self._generate_pdf_report_for_student(student_data)
                    task_ids.append(student_result)
                
                result['batch_task_ids'] = task_ids
                result['batch_status'] = f'Processing batch of {len(data)} students'
            else:
                # Single student processing
                student_result = self._generate_pdf_report_for_student(data)
                result.update(student_result)
            
            return Response(result, status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_pdf_report_for_student(self, student_data):
        """Generate PDF report for a single student."""
        pdf_task_id = str(uuid.uuid4())
        ReportTask.objects.create(task_id=pdf_task_id)
        
        # Generate temporary HTML first (not exposed in response)
        temp_html_task_id = str(uuid.uuid4())
        ReportTask.objects.create(task_id=temp_html_task_id)
        
        generate_html_report.delay(
            temp_html_task_id,
            student_data['student_id'],
            student_data['events']
        )
        
        # Then generate PDF based on that HTML
        generate_pdf_report.delay(
            pdf_task_id,
            student_data['student_id'],
            temp_html_task_id
        )
        
        return {'pdf_task_id': pdf_task_id}
    
    def _extract_data(self, request):
        """Extract and validate data from request, handling both file uploads and direct JSON."""
        # Same implementation as in GenerateReportView
        if 'file' in request.FILES:
            file = request.FILES['file']
            if not file.name.endswith('.json'):
                return Response(
                    {"error": "Only JSON files are allowed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                path = default_storage.save(f'tmp/{file.name}', ContentFile(file.read()))
                with default_storage.open(path) as f:
                    data = json.load(f)
                default_storage.delete(path)
                
                if isinstance(data, list):
                    for student in data:
                        if not all(key in student for key in ['student_id', 'events', 'namespace']):
                            return Response(
                                {"error": "Invalid student data format. Required fields: namespace, student_id, events"},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    return data
                
                if not all(key in data for key in ['student_id', 'events', 'namespace']):
                    return Response(
                        {"error": "Invalid payload format. Required fields: namespace, student_id, events"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return data
                
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid JSON file"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        data = request.data
        
        if isinstance(data, list):
            for student in data:
                if not all(key in student for key in ['student_id', 'events', 'namespace']):
                    return Response(
                        {"error": "Invalid student data format. Required fields: namespace, student_id, events"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return data
        
        if not all(key in data for key in ['student_id', 'events', 'namespace']):
            return Response(
                {"error": "Invalid payload format. Required fields: namespace, student_id, events"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return data



class GetHTMLReportView(APIView):
    def get(self, request, task_id):
        try:
            task = ReportTask.objects.get(task_id=task_id)
            
            if task.status == 'completed':
                report = HTMLReport.objects.get(task=task)
                return Response({
                    "status": "completed",
                    "html": report.content,
                    "student_id": report.student_id
                })
            
            return Response({"status": task.status})

        except ReportTask.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class GetPDFReportView(APIView):
    def get(self, request, task_id):
        try:
            task = ReportTask.objects.get(task_id=task_id)
            
            if task.status == 'completed':
                report = PDFReport.objects.get(task=task)
                if report.file_data:
                    response = FileResponse(
                        io.BytesIO(report.file_data),
                        content_type='application/pdf'
                    )
                    response['Content-Disposition'] = f'attachment; filename="report_{task_id}.pdf"'
                    return response
                elif report.file_path:
                    # Serve file from disk
                    with open(report.file_path, 'rb') as f:
                        response = FileResponse(f, content_type='application/pdf')
                        response['Content-Disposition'] = f'attachment; filename="report_{task_id}.pdf"'
                        return response
            
            return Response({"status": task.status})

        except ReportTask.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GenerateReportView(APIView):
    """
    API view to generate both HTML and PDF reports with a single call.
    
    Accepts both direct JSON payload and file uploads.
    Returns task IDs for both HTML and PDF reports.
    """
    parser_classes = (MultiPartParser, JSONParser)
    
    def post(self, request):
        try:
            # Extract the data from either JSON payload or uploaded file
            data = self._extract_data(request)
            if isinstance(data, Response):  # Error case
                return data
            
            # Optional format parameter to specify which reports to generate
            # report_format = request.query_params.get('format', 'both').lower()
            report_format = request.headers.get('format', 'both').lower()
           
            result = {}
            
            # Generate reports for each student in the data
            if isinstance(data, list):
                # Batch processing
                task_ids = []
                for student_data in data:
                    student_result = self._generate_reports_for_student(
                        student_data, 
                        report_format
                    )
                    task_ids.append(student_result)
                
                result['batch_task_ids'] = task_ids
                result['batch_status'] = f'Processing batch of {len(data)} students'
            else:
                # Single student processing
                student_result = self._generate_reports_for_student(
                    data, 
                    report_format
                )
                result.update(student_result)
            
            return Response(result, status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_reports_for_student(self, student_data, report_format):
        """Generate reports for a single student."""
        result = {}
        
        # Generate HTML report if requested
        if report_format in ['html', 'both']:
            html_task_id = str(uuid.uuid4())
            ReportTask.objects.create(task_id=html_task_id)
            
            generate_html_report.delay(
                html_task_id,
                student_data['student_id'],
                student_data['events']
            )
            result['html_task_id'] = html_task_id
        
        # Generate PDF report if requested
        if report_format in ['pdf', 'both']:
            pdf_task_id = str(uuid.uuid4())
            ReportTask.objects.create(task_id=pdf_task_id)
            
            # If we've already generated an HTML report, use its task_id
            html_dependency = result.get('html_task_id') if report_format == 'both' else None
            
            if html_dependency:
                # When generating both, make PDF depend on HTML completion
                generate_pdf_report.delay(
                    pdf_task_id,
                    student_data['student_id'],
                    html_dependency
                )
            else:
                # When generating only PDF, create HTML internally first
                temp_html_task_id = str(uuid.uuid4())
                ReportTask.objects.create(task_id=temp_html_task_id)
                
                # Generate HTML first (not exposed in response)
                generate_html_report.delay(
                    temp_html_task_id,
                    student_data['student_id'],
                    student_data['events']
                )
                
                # Then generate PDF based on that HTML
                generate_pdf_report.delay(
                    pdf_task_id,
                    student_data['student_id'],
                    temp_html_task_id
                )
            
            result['pdf_task_id'] = pdf_task_id
        
        return result
    
    def _extract_data(self, request):
        """Extract and validate data from request, handling both file uploads and direct JSON."""
        # Handle JSON file upload
        if 'file' in request.FILES:
            file = request.FILES['file']
            if not file.name.endswith('.json'):
                return Response(
                    {"error": "Only JSON files are allowed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Save temporarily
                path = default_storage.save(f'tmp/{file.name}', ContentFile(file.read()))
                with default_storage.open(path) as f:
                    data = json.load(f)
                default_storage.delete(path)  # Clean up
                
                # Validate the data structure
                if isinstance(data, list):
                    for student in data:
                        if not all(key in student for key in ['student_id', 'events', 'namespace']):
                            return Response(
                                {"error": "Invalid student data format. Required fields: namespace, student_id, events"},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    return data
                
                # Handle single student case
                if not all(key in data for key in ['student_id', 'events', 'namespace']):
                    return Response(
                        {"error": "Invalid payload format. Required fields: namespace, student_id, events"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return data
                
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid JSON file"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Handle direct JSON payload
        data = request.data
        
        # Handle array of students
        if isinstance(data, list):
            for student in data:
                if not all(key in student for key in ['student_id', 'events', 'namespace']):
                    return Response(
                        {"error": "Invalid student data format. Required fields: namespace, student_id, events"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return data
        
        # Handle single student
        if not all(key in data for key in ['student_id', 'events', 'namespace']):
            return Response(
                {"error": "Invalid payload format. Required fields: namespace, student_id, events"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return data



class GetAIInsightsView(APIView):
    def get(self, request, task_id):
        try:
            task = ReportTask.objects.get(task_id=task_id)
            
            if task.status != 'completed':
                return Response(
                    {"status": "Report not ready"},
                    status=status.HTTP_425_TOO_EARLY
                )
                
            # Directly generate insights
            insights = generate_insights(task_id)
            html_report = HTMLReport.objects.filter(task=task).first()
            student_id = html_report.student_id
            return Response({
                "student_id": student_id,
                "status": "Insights generated",
                "insights": insights,
                "monitor_url": f"/assignment/html/{task_id}"
            })
            
        except ReportTask.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )