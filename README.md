# Feedback Report Generator

A Django-based service for generating student activity reports in HTML/PDF formats with async processing and AI insights.

## 📥 Installation

### Prerequisites
- Docker 20.10+
- Docker Compose 2.5+
- Python 3.9+
- Poetry 1.4+

### Clone the Repository
```bash
git clone https://github.com/Afringowhar/FeedbackReport.git
cd feedback-report-generator
```

## 🚀 Quick Start
1. **Set up environment variables**:
   ```bash
   cp app/.env.example app/.env
   # Edit the .env file with your credentials
   ```

2. **Build and run containers**:
   ```bash
   docker-compose up -d --build
   ```

3. **Apply migrations**:
   ```bash
   docker-compose exec web python manage.py makemigration
   docker-compose exec web python manage.py migrate
   ```

4. **Create admin user** (optional):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## 🌸 Flower Monitoring
Access task monitoring at:
```
http://localhost:5555
```

Key features:
- Real-time task status
- Worker management
- Task history and statistics

## 🗄️ PGAdmin (Optional)
To access PostgreSQL database:
1. Uncomment pgadmin service in docker-compose.yml
2. Access at `http://localhost:5050`
3. Login with:
   ```
   Email: admin@example.com
   Password: admin
   ```
4. Connect to server:
   - Name: `feedback_reports`
   - Host: `db`
   - Username: `django_user`
   - Password: `yourpassword`

## 📁 File Structure

```
/feedbackreport
├── /app
│   ├── /core
│   │   ├── /__pycache__                # Python compiled bytecode cache
│   │   ├── __init__.py                 # Python package initialization
│   │   ├── asgi.py                     # ASGI config for async server gateway
│   │   ├── celery.py                   # Celery configuration file
│   │   ├── settings.py                 # Django project settings
│   │   ├── urls.py                     # Main URL routing configuration
│   │   ├── wsgi.py                     # WSGI config for production deployment
│   │   └── /media/reports/pdf          # Storage for generated PDF files
│   ├── /reports
│   │   ├── /__pycache__                # Python compiled bytecode cache
│   │   ├── /migrations                 # Database migration files
│   │   ├── /templates/reports          # HTML templates directory
│   │   │   └── student_report.html     # Template for student reports
│   │   ├── __init__.py                 # Python package initialization
│   │   ├── admin.py                    # Django admin configuration
│   │   ├── apps.py                     # App configuration
│   │   ├── llm_integration.py          # Gemini AI integration module
│   │   ├── models.py                   # Database models definition
│   │   ├── tasks.py                    # Celery tasks definitions
│   │   ├── tests.py                    # Test cases
│   │   ├── urls.py                     # App-specific URL routing
│   │   └── views.py                    # API view definitions
│   ├── .env                            # Environment variables
│   ├── api.yaml                         # Application YAML configuration (if applicable)
│   ├── get-docker.sh                   # Docker installation helper script
│   ├── manage.py                       # Django command-line utility
│   ├── poetry.lock                     # Poetry dependency lock file
│   └── pyproject.toml                  # Python project dependencies and config
├── docker-compose.yml                  # Multi-container Docker configuration
├── Dockerfile                          # Docker container build instructions
└── README.md                           # Project documentation
```

### Key File Descriptions:

1. **Core Application Files**:
   - `celery.py`: Configures Celery for asynchronous task processing
   - `settings.py`: Contains Django project settings (database, middleware, etc.)
   - `urls.py`: Defines the main URL routes for the project

2. **Reports App Files**:
   - `models.py`: Defines database models (ReportTask, HTMLReport, PDFReport)
   - `tasks.py`: Contains Celery tasks for report generation
   - `views.py`: Implements API endpoints for report processing
   - `llm_integration.py`: Handles Gemini AI analysis integration

3. **Configuration Files**:
   - `.env`: Stores environment variables (API keys, database credentials)
   - `docker-compose.yml`: Defines services (Django, PostgreSQL, Redis, etc.)
   - `Dockerfile`: Instructions for building the Django container

4. **Template Files**:
   - `student_report.html`: Jinja2 template for HTML report generation

5. **Build/Deployment Files**:
   - `pyproject.toml`: Python project metadata and dependencies
   - `poetry.lock`: Exact versions of all dependencies
   - `get-docker.sh`: Helper script for Docker setup (if needed)

   - `README.md`: Project documentation and setup instructions   



## 🛠️ Tech Stack
```
| Component          | Technology               |
|--------------------|--------------------------|
| Backend Framework  | Django 4.2 + DRF         |
| Database           | PostgreSQL 16            |
| Async Processing   | Celery + Redis           |
| Task Monitoring    | Flower                   |
| PDF Generation     | ReportLab                |
| AI Integration     | Google Gemini            |
| Containerization   | Docker                   |
| Package Management | Poetry                   |
```

## 📊 Database Models
![image](https://github.com/user-attachments/assets/60712c73-bec2-4688-99a8-af613a0a7f5b)



## 🌐 API Endpoints
## API Endpoints Documentation

| Endpoint | Method | Description | Input | Output |
|----------|--------|-------------|-------|--------|
| `/assignment/html` | POST | Generate HTML report | JSON payload or `.json` file with student events | `{html_task_id: string}` or with batch task IDs |
| `/assignment/html/<task_id>` | GET | Get HTML report status/content | Task ID in URL | Completed: `{status, html, student_id}`<br>Pending: `{status}` |
| `/assignment/pdf` | POST | Generate PDF report | JSON payload or `.json` file with student events | `{pdf_task_id: string}` or with batch task IDs |
| `/assignment/pdf/<task_id>` | GET | Download PDF report | Task ID in URL | PDF file or `{status}` if pending |
| `/assignment/report` | POST | Generate html, pdf or both reports | JSON payload or `.json` file + optional `format` header (`html`/`pdf`/`both`) | `{html_task_id, pdf_task_id}` or with batch task IDs |
| `/assignment/insights/<task_id>` | GET | Get AI insights for report | Task ID in URL | `{student_id, status, insights}` |

**Sample Input (JSON):**
```json
{
    "namespace": "course101",
    "student_id": "stu123",
    "events": [
        {
            "type": "code_save",
            "unit": 3,
            "created_time": "2024-01-01T12:00:00Z"
        }
    ]
}
```

## 🛠️ Maintenance
```bash
# View logs
docker-compose logs -f web

# Rebuild containers
docker-compose up -d --build

# Run tests
docker-compose exec web python manage.py test

# Access database shell
docker-compose exec db psql -U django_user -d feedback_reports
```

Made with love by [Afrin Gowhar](https://www.linkedin.com/in/afrin-gowhar/overlay/contact-info/) and powered by [IIT Madras BS Degree]
