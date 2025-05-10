from django.utils import timezone
from core.settings import GEMINI_API_KEY
import google.generativeai as genai
from .models import ReportTask, HTMLReport

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)  # Store in Django settings
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_insights(task_id):
    """
    Generates AI insights using existing report data as context
    """
    try:
        # 1. Get all related data from existing tables
        task = ReportTask.objects.get(task_id=task_id)
        html_report = HTMLReport.objects.filter(task=task).first()
        

        # 2. Prepare context prompt
        prompt = f"""
        Analyze this student's coding activity report:
        
        - Student ID: {html_report.student_id if html_report else 'N/A'}
        - Task Status: {task.status}
        - Events Processed: {len(html_report.content.split('->')) if html_report else 0}
        
        HTML Content Excerpt:
        {html_report.content if html_report else 'No HTML report'}
        
        Generate:
        1. Three key observations about the student's work patterns
        2. Suggested areas for improvement
        3. Estimated time spent per unit (if timestamps are available)
        """

        # 3. Get AI response
        response = model.generate_content(prompt)
        
        return {
            'insights': response.text,
            'metadata': {
                'task_id': str(task_id),
                'generated_at': timezone.now()
            }
        }

    except Exception as e:
        return {'error': str(e)}