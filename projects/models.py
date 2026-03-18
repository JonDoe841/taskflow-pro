from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.
class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    name = models.CharField(max_length = 200)
    description = models.TextField()
    created_by = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        related_name='profiles'
        )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMembership',
        related_name='projects'
    )
    technologies = models.ManyToManyField(
        'Technology',
        blank=True,
        related_name='projects'
    )
    start_date = models.DateField(default=timezone.now)
    deadline = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default='planing')
    priority = models.CharField(max_length=20,
                                choices=PRIORITY_CHOICES,
                                default='medium')
    budget = models.DecimalField(max_digits=12,
                                 decimal_places=2,
                                 null=True,
                                 blank=True)
    hours_estimated = models.IntegerField(default=0)
    hours_logged = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    @property
    def progress_percentage(self):
        if self.hours_estimated > 0:
            return min(100, int((self.hours_logged / self.hours_estimated) * 100))
        return 0

class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('developer', 'Developer'),
        ('reviewer', 'Reviewer'),
        ('observer', 'Observer'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,
                            default='developer')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    contribution_hours = models.IntegerField(default=0)

    class Meta:
        unique_together = ['project', 'user']

    def __str__(self):
        return (f"{self.user.username} - {self.project.name}"
                f" ({self.role})")


class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50, default='other')
    icon = models.CharField(max_length=50, blank=True,
                            help_text="FontAwesome icon class")

    def __str__(self):
        return self.name




