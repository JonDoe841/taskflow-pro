from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from projects.models import Project

# Create your models here.
class TaskTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6c757d')

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_tasks')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')

    dependencies = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_tasks')
    tags = models.ManyToManyField(TaskTag, blank=True, related_name='tasks')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    logged_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ['-priority', 'due_date']
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'done' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def is_overdue(self):
        return self.due_date < timezone.now() and self.status != 'done'


class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"

