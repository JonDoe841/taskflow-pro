from django.db import models
from django.conf import settings
# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='created_teams')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     through='TeamMembership',
                                     related_name='teams')
    lead = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL,
                             null=True, related_name='led_teams')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TeamMembership(models.Model):

    ROLE_CHOICES = [
        ('lead', 'Team Lead'),
        ('member', 'Team Member'),
        ('intern', 'Intern'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    role = models.CharField(max_length=20,
                            choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        unique_together = ['team', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"