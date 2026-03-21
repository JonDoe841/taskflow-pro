from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import timedelta

from analytics.models import Report
from projects.models import Project


@shared_task
def generate_weekly_reports():
    reports_generated = 0

    now = timezone.now()
    week_ago = now - timedelta(days=7)

    for project in Project.objects.filter(status='active'):

        tasks = project.tasks.all()

        tasks_created = tasks.filter(created_at__gte=week_ago).count()
        tasks_completed = tasks.filter(completed_at__gte=week_ago).count()

        tasks_by_status_qs = tasks.values('status').annotate(count=Count('id'))
        tasks_by_status = {
            item['status']: item['count']
            for item in tasks_by_status_qs
        }

        total_hours = tasks.aggregate(total=Sum('logged_hours'))['total'] or 0

        report_data = {
            'project_id': project.id,
            'project_name': project.name,
            'generated_at': now,
            'period_start': week_ago,
            'period_end': now,
            'metrics': {
                'tasks_created': tasks_created,
                'tasks_completed': tasks_completed,
                'tasks_by_status': tasks_by_status,
                'hours_logged': total_hours,
                'member_activity': get_member_activity(project, week_ago),
            }
        }

        Report.objects.create(
            project=project,
            report_type='weekly',
            data=report_data,
            generated_by=None
        )

        reports_generated += 1

    return f"Generated {reports_generated} weekly reports"


def get_member_activity(project, week_ago):
    member_activity = []

    for membership in project.projectmembership_set.select_related('user'):
        user = membership.user

        tasks_completed = user.assigned_tasks.filter(
            project=project,
            completed_at__gte=week_ago
        ).count()

        member_activity.append({
            'user_id': user.id,
            'username': user.username,
            'tasks_completed': tasks_completed,
            'role': membership.role
        })

    return member_activity