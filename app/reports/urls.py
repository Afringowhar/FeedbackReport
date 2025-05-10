from django.urls import path
from .views import (
    GenerateReportView,
    GenerateHTMLReportView,
    GeneratePDFReportView,
    GetHTMLReportView,
    GetPDFReportView,
    GetAIInsightsView
)

urlpatterns = [
    path('assignment/json', GenerateReportView.as_view()),
    path('assignment/html', GenerateHTMLReportView.as_view()),
    path('assignment/pdf', GeneratePDFReportView.as_view()),
    path('assignment/html/<uuid:task_id>', GetHTMLReportView.as_view()),
    path('assignment/pdf/<uuid:task_id>', GetPDFReportView.as_view()),
    path('assignment/ai/<uuid:task_id>', GetAIInsightsView.as_view())
]