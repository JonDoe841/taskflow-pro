import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskflow_pro.settings')

app = Celery('taskflow_pro')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-daily-task-summary': {
        'task': 'tasks.tasks.send_daily_task_summary',
        'schedule': crontab(hour=9, minute=0),
    },
    'generate-weekly-reports': {
        'task': 'analytics.tasks.generate_weekly_reports',
        'schedule': crontab(day_of_week='mon', hour=1, minute=0),
    },
    'cleanup-old-notifications': {
        'task': 'accounts.tasks.cleanup_old_notifications',
        'schedule': crontab(day_of_month='1', hour=2, minute=0),
    },
}




