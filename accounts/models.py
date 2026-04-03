from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    date_joined_company = models.DateField(default=timezone.now)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @property
    def total_projects(self):
        return self.projects.count()

    @property
    def total_tasks(self):
        return self.assigned_tasks.count()

    @property
    def completed_tasks(self):
        return self.assigned_tasks.filter(status='done').count()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    github_profile = models.URLField(blank=True)
    linkedin_profile = models.URLField(blank=True)
    notification_preferences = models.JSONField(default=dict)  # Keep as JSONField

    def __str__(self):
        return f"Profile for {self.user.username}"