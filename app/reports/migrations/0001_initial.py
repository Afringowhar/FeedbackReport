# Generated by Django 5.2 on 2025-05-09 09:55

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReportTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('task_id', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['status'], name='idx_report_task_status'), models.Index(fields=['created_at'], name='idx_report_task_created_at')],
            },
        ),
        migrations.CreateModel(
            name='PDFReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_data', models.BinaryField(blank=True, null=True)),
                ('file_path', models.CharField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_report', to='reports.reporttask')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['task'], name='idx_pdf_report_task')],
            },
        ),
        migrations.CreateModel(
            name='HTMLReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='html_report', to='reports.reporttask')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['task'], name='idx_html_report_task')],
            },
        ),
    ]
