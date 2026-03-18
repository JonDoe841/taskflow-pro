from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# Create your models here.
class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    date_joined_company = models.DateField(default=timezone.now)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile')
    skills = models.TextField(help_text="Comma-separated skills",
                              blank=True)
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    github_profile = models.URLField(blank=True)
    linkedin_profile = models.URLField(blank=True)
    notifications = models.JSONField(default=dict)

    def __str__(self):
        return f"Profile for {self.user.username}"

