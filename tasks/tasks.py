from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import Task
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_task_assignment_email(task_id, assigned_to_email, assigned_by_username):
    try:
        task = Task.objects.get(id=task_id)
        subject = f'New Task Assigned: {task.title}'

        context = {
            'task': task,
            'assigned_by': assigned_by_username,
            'project': task.project.name,
            'due_date': task.due_date,
        }
        html_message = render_to_string('emails/task_assigned.html', context)
        plain_message = render_to_string('emails/task_assigned.txt', context)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [assigned_to_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Task assignment email sent for task {task_id}")
        return f"Email sent successfully to {assigned_to_email}"
    except Task.DoesNotExist:
        logger.error(f"Task {task_id} not found")
        return f"Task {task_id} not found"
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise

@shared_task
def send_daily_task_summary():
    from django.contrib.auth import get_user_model
    User = get_user_model()

    tomorrow = timezone.now() + timedelta(days=1)
    users_with_tasks = User.objects.filter(
        assigned_tasks__due_date__date=tomorrow.date(),
        assigned_tasks__status__in=['todo', 'in_progress']
    ).distinct()

    for user in users_with_tasks:
        tasks_due_tomorrow = user.assigned_tasks.filter(
            due_date__date=tomorrow.date(),
            status__in=['todo', 'in_progress']
        )
        if tasks_due_tomorrow.exists():
            subject = f'Task Summary: {tasks_due_tomorrow.count()} tasks due tomorrow'
            context = {
                'user': user,
                'tasks': tasks_due_tomorrow,
                'tomorrow': tomorrow.date(),
            }

            html_message = render_to_string('emails/daily_summary.html', context)

            send_mail(
                subject,
                '',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

    return f"Sent daily summaries to {users_with_tasks.count()} users"
@shared_task
def generate_task_report(project_id, requested_by):
    from projects.models import Project
    import time
    import csv
    from io import StringIO
    time.sleep(5)
    try:
        project = Project.objects.get(id=project_id)
        tasks = project.tasks.all()
        report_data = {
            'project_name': project.name,
            'total_tasks': tasks.count(),
            'completed_tasks': tasks.filter(status='done').count(),
            'in_progress_tasks': tasks.filter(status='in_progress').count(),
            'todo_tasks': tasks.filter(status='todo').count(),
            'total_hours_logged': sum(task.logged_hours for task in tasks),
            'estimated_hours_remaining': sum
                (task.estimated_hours for task in tasks.filter(status__in=['todo', 'in_progress'])),
            'tasks_by_priority': {
                'high': tasks.filter(priority='high').count(),
                'medium': tasks.filter(priority='medium').count(),
                'low': tasks.filter(priority='low').count(),
            }
        }
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Task Title', 'Status', 'Priority',
                         'Assigned To', 'Due Date', 'Hours Logged'])
        for task in tasks:
            writer.writerow([
                task.title,
                task.get_status_display(),
                task.get_priority_display(),
                task.assigned_to.username if task.assigned_to else 'Unassigned',
                task.due_date.strftime('%Y-%m-%d'),
                task.logged_hours,
            ])
        logger.info(f"Report generated for project {project.name}")
        return report_data
    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found")
        return None