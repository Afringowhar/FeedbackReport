from django.contrib import admin
from .models import ReportTask, HTMLReport, PDFReport

@admin.register(ReportTask)
class ReportTaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'status', 'created_at', 'started_at', 'completed_at')
    readonly_fields = ('task_id', 'created_at', 'started_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('task_id',)

@admin.register(HTMLReport)
class HTMLReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_task_id', 'created_at', 'content_preview')
    readonly_fields = ('content_preview', 'task', 'created_at')
    
    def get_task_id(self, obj):
        return obj.task.task_id
    get_task_id.short_description = 'Task ID'
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(PDFReport)
class PDFReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_task_id', 'created_at', 'storage_type')
    readonly_fields = ('task', 'created_at', 'storage_type')
    
    def get_task_id(self, obj):
        return obj.task.task_id
    get_task_id.short_description = 'Task ID'
    
    def storage_type(self, obj):
        return "Database" if obj.file_data else "File Path" if obj.file_path else "Unknown"
    storage_type.short_description = 'Storage Type'