from django.db import models

from accounts.models import User
from projects.models import Project


# Create your models here.
class Report(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=50)
    data = models.JSONField()
    generated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)