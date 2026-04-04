# TaskFlow Pro - Collaborative Task Management Platform

![TaskFlow Pro](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Overview

TaskFlow Pro is a comprehensive task management platform designed for modern teams to collaborate effectively on projects, track progress, and optimize workflow. Built with Django and Django REST Framework, it provides a robust solution for project management, team collaboration, and productivity tracking. here is also link to render[https://taskflow-pro-rgqe.onrender.com/]

## ✨ Features

### Core Functionality
- **User Authentication**: Registration, login, logout with extended user profiles
- **Project Management**: Create, update, delete, and track projects with progress monitoring
- **Task Management**: Assign tasks, track status, set priorities, and add comments
- **Team Collaboration**: Create teams, manage members, assign roles
- **Analytics Dashboard**: Visual insights into project progress and team performance
- **Blog System**: Share updates and tips with built-in blog functionality

### Technical Features
- **RESTful API**: Complete API with token authentication and Swagger documentation
- **Asynchronous Processing**: Celery tasks for email notifications and report generation
- **Responsive Design**: Bootstrap 5 with mobile-first approach
- **Security**: CSRF protection, XSS prevention, SQL injection protection
- **Testing**: 39+ comprehensive tests covering models, views, and forms

## 🛠 Tech Stack

### Backend
- **Django 5.0** - Web framework
- **Django REST Framework** - API development
- **Celery 5.3** - Async task processing
- **Redis** - Message broker & cache
- **PostgreSQL** - Database
- **Gunicorn** - WSGI HTTP server

### Frontend
- **Bootstrap 5** - CSS framework
- **Font Awesome 6** - Icons
- **Chart.js** - Data visualization
- **Django Templates** - Server-side rendering

### DevOps
- **Render** - Cloud deployment
- **GitHub Actions** - CI/CD pipeline
- **WhiteNoise** - Static file serving

## 📁 Project Structure
taskflow-pro/
├── accounts/ # User authentication & profiles
│ ├── models.py # Custom User, UserProfile
│ ├── views.py # Registration, login, profile views
│ ├── forms.py # User forms with validations
│ ├── urls.py # Account URL routes
│ └── tests.py # 18 tests
│
├── projects/ # Project management
│ ├── models.py # Project, Technology, ProjectMembership
│ ├── views.py # CRUD views for projects
│ ├── forms.py # Project forms
│ ├── urls.py # Project URL routes
│ ├── tests.py # 11 tests
│ └── templatetags/ # Custom template filters
│ └── project_tags.py # status_color, priority_color filters
│
├── tasks/ # Task management
│ ├── models.py # Task, TaskComment, TaskTag
│ ├── views.py # Task CRUD views
│ ├── forms.py # Task forms
│ ├── urls.py # Task URL routes
│ └── tests.py # 10 tests
│
├── teams/ # Team collaboration
│ ├── models.py # Team, TeamMembership
│ ├── views.py # Team CRUD views
│ ├── forms.py # Team forms
│ ├── urls.py # Team URL routes
│ └── tests.py # Team tests
│
├── analytics/ # Reports & analytics
│ ├── models.py # Report model
│ ├── views.py # Dashboard and reports
│ ├── urls.py # Analytics URL routes
│ ├── tests.py # Analytics tests
│ └── templates/ # Analytics templates
│ └── analytics/
│ ├── dashboard.html
│ ├── reports.html
│ └── report_detail.html
│
├── api/ # REST API
│ ├── serializers.py # DRF serializers
│ ├── views.py # API endpoints
│ ├── permissions.py # Custom permissions
│ ├── urls.py # API routes
│ └── tests.py # API tests
│
├── core/ # Core functionality
│ ├── models.py # BlogPost, BlogComment
│ ├── views.py # Home, about, contact, blog
│ ├── forms.py # Contact form, comment form
│ ├── urls.py # Core routes
│ └── tests.py # Core tests
│
├── taskflow_pro/ # Project settings
│ ├── init.py # Celery app initialization
│ ├── settings.py # Development settings
│ ├── celery.py # Celery configuration
│ └── urls.py # Main URL configuration
│
├── templates/ # HTML templates (40+)
│ ├── base.html # Base template with navbar/footer
│ ├── base_public.html # Public section template
│ ├── accounts/ # Account templates
│ ├── projects/ # Project templates
│ ├── tasks/ # Task templates
│ ├── teams/ # Team templates
│ ├── analytics/ # Analytics templates
│ ├── core/ # Core page templates
│ ├── emails/ # Email templates
│ └── includes/ # Reusable partials
│ ├── navbar.html
│ ├── footer.html
│ ├── messages.html
│ └── sidebar.html
│
├── static/ # Static files
│ ├── css/
│ │ └── style.css # Custom styles
│ ├── js/
│ │ └── main.js # Custom JavaScript
│ └── images/ # Images and favicon
│
├── media/ # User uploaded files (avatars, etc.)
│
├── requirements.txt # Python dependencies
├── .env.example # Environment variables example
├── .gitignore # Git ignore rules
├── manage.py # Django management script
├── Procfile # Render/Heroku deployment config
├── runtime.txt # Python version for deployment
└── README.md # Project documentation

### Key Files Explained

| File | Purpose |
|------|---------|
| `manage.py` | Django's command-line utility for administrative tasks |
| `requirements.txt` | Python package dependencies |
| `.env.example` | Template for environment variables |
| `Procfile` | Deployment instructions for Render/Heroku |
| `celery.py` | Celery configuration for async tasks |
| `urls.py` | Main URL routing configuration |
| `settings.py` | Django project settings |

## 🚀 Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+ (for Celery)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/taskflow-pro.git
cd taskflow-pro
Step 2: Create Virtual Environment
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
Step 3: Install Dependencies
bash
pip install -r requirements.txt
Step 4: Configure Environment Variables
bash
cp .env.example .env
Edit .env with your configuration:

env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_NAME=taskflow_db
DATABASE_USER=postgres
DATABASE_PASSWORD=yourpassword
DATABASE_HOST=localhost
DATABASE_PORT=5432

REDIS_URL=redis://localhost:6379
Step 5: Create Database
bash
# PostgreSQL
createdb taskflow_db
Step 6: Run Migrations
bash
python manage.py makemigrations
python manage.py migrate
Step 7: Create Superuser
bash
python manage.py createsuperuser
Step 8: Create User Groups
bash
python manage.py shell
python
from django.contrib.auth.models import Group
Group.objects.get_or_create(name='Project Managers')
Group.objects.get_or_create(name='Team Members')
exit()
Step 9: Run Development Server
bash
python manage.py runserver
Visit http://127.0.0.1:8000/

Step 10: Start Celery Worker (Optional)
bash
# In a new terminal
celery -A taskflow_pro worker --loglevel=info
🧪 Running Tests
bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test projects
python manage.py test tasks

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
Total Tests: 39+ (all passing)

📚 API Documentation
Base URL
text
http://localhost:8000/api/
Authentication
API uses Token Authentication. Obtain token:

text
POST /api/auth/token/
Endpoints
Method	Endpoint	Description	Permissions
GET	/api/projects/	List projects	Public
POST	/api/projects/	Create project	Authenticated
GET	/api/projects/{id}/	Project details	Public
PUT	/api/projects/{id}/	Update project	Owner/Manager
DELETE	/api/projects/{id}/	Delete project	Owner
GET	/api/tasks/	List tasks	Authenticated
POST	/api/tasks/	Create task	Project Member
GET	/api/tasks/{id}/	Task details	Project Member
GET	/api/users/me/	Current user	Authenticated
GET	/api/dashboard/	Dashboard stats	Authenticated
Interactive Documentation
Swagger UI: /api/docs/

ReDoc: /api/redoc/

Example API Request
bash
# Get all projects
curl -X GET http://localhost:8000/api/projects/

# Create a task
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Task",
    "project": 1,
    "due_date": "2025-04-01T00:00:00Z",
    "priority": "high"
  }'
🔧 Configuration
Environment Variables
Variable	Description	Default
DEBUG	Debug mode	True
SECRET_KEY	Django secret key	Required
ALLOWED_HOSTS	Allowed hosts	localhost,127.0.0.1
DATABASE_NAME	Database name	taskflow_db
DATABASE_USER	Database user	postgres
DATABASE_PASSWORD	Database password	Required
REDIS_URL	Redis URL	redis://localhost:6379
🚀 Deployment
Deploy to Render
Push code to GitHub repository

Create account on render.com

Click "New +" → "Web Service"

Connect your GitHub repository

Use these settings:

Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate

Start Command: gunicorn taskflow_pro.wsgi:application

Add environment variables from .env

Click "Create Web Service"

Deploy to Heroku
bash
# Install Heroku CLI
heroku create taskflow-pro
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku open
📝 User Groups & Permissions
Group	Permissions
Project Managers	Full CRUD access to projects, tasks, teams
Team Members	View projects, create/update tasks, view teams
🧪 Test Credentials (Development)
text
Username: testuser
Password: testpass123
🤝 Contributing
Fork the repository

Create feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
This project is licensed under the MIT License.

👨‍💻 Author
Your Name

GitHub: @yourusername

LinkedIn: Your Profile

🙏 Acknowledgments
Django Documentation

Django REST Framework

Bootstrap Team

SoftUni Django Advanced Course
