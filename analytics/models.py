from django.db import models
from django.conf import settings
from django.utils import timezone
from projects.models import Project


# Create your models here.
class Report(models.Model):
    REPORT_TYPES = [
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('project', 'Project Report'),
        ('team', 'Team Report'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    data = models.JSONField(default=dict)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    period_start = models.DateTimeField(default=timezone.now)
    period_end = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at.date()}"
