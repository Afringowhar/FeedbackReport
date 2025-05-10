# from django.db import models
# from django.utils import timezone

# class ReportTask(models.Model):
#     """Stores task metadata and status"""
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('processing', 'Processing'),
#         ('completed', 'Completed'),
#         ('failed', 'Failed'),
#     ]
    
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='pending'
#     )
#     created_at = models.DateTimeField(default=timezone.now)
#     started_at = models.DateTimeField(null=True, blank=True)
#     completed_at = models.DateTimeField(null=True, blank=True)
#     task_id = models.CharField(max_length=255, unique=True)  # Celery task ID
    
#     class Meta:
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['status'], name='idx_report_task_status'),
#             models.Index(fields=['created_at'], name='idx_report_task_created_at'),
#         ]

    

# class HTMLReport(models.Model):
#     """Stores generated HTML content"""
#     task = models.OneToOneField(
#         ReportTask,
#         on_delete=models.CASCADE,
#         related_name='html_report'
#     )
#     content = models.TextField()  # HTML content
#     created_at = models.DateTimeField(default=timezone.now)
    
#     class Meta:
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['task'], name='idx_html_report_task'),
#         ]

# class PDFReport(models.Model):
#     """Stores PDF binary data or file reference"""
#     task = models.OneToOneField(
#         ReportTask,
#         on_delete=models.CASCADE,
#         related_name='pdf_report'
#     )
#     # Option 1: Store file in database (for small files)
#     file_data = models.BinaryField(null=True, blank=True)
    
#     # Option 2: Store file path (for large files)
#     file_path = models.CharField(max_length=500, null=True, blank=True)
    
#     created_at = models.DateTimeField(default=timezone.now)
    
#     class Meta:
#         ordering = ['-created_at']
#         indexes = [
#             models.Index(fields=['task'], name='idx_pdf_report_task'),
#         ]


from django.db import models
from django.utils import timezone

class ReportTask(models.Model):
    """Stores task metadata and status"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    task_id = models.CharField(max_length=255, unique=True)  # Celery task ID
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_report_task_status'),
            models.Index(fields=['created_at'], name='idx_report_task_created_at'),
        ]

class HTMLReport(models.Model):
    """Stores generated HTML content"""
    task = models.OneToOneField(
        ReportTask,
        on_delete=models.CASCADE,
        related_name='html_report'
    )
    content = models.TextField()  # HTML content
    created_at = models.DateTimeField(default=timezone.now)
    student_id = models.CharField(max_length=255, null=True, blank=True)  # Added field
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task'], name='idx_html_report_task'),
        ]

class PDFReport(models.Model):
    """Stores PDF binary data or file reference"""
    task = models.OneToOneField(
        ReportTask,
        on_delete=models.CASCADE,
        related_name='pdf_report'
    )
    # Option 1: Store file in database (for small files)
    file_data = models.BinaryField(null=True, blank=True)
    
    # Option 2: Store file path (for large files)
    file_path = models.CharField(max_length=500, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    student_id = models.CharField(max_length=255, null=True, blank=True)  # Added field
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task'], name='idx_pdf_report_task'),
        ]