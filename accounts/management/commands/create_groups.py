from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from projects.models import Project, Technology
from tasks.models import Task
from teams.models import Team

class Command(BaseCommand):
    help = 'Create user groups and assign permissions'
    def handle(self, *args, **kwargs):
        project_manager_group, created = Group.objects.get_or_create(name='Project Manager')
        team_member_group, created = Group.objects.get_or_create(name='Team Members')

        project_ct = ContentType.objects.get_for_model(Project)
        task_ct = ContentType.objects.get_for_model(Task)
        team_ct = ContentType.objects.get_for_model(Team)

        project_permissions = Permission.objects.filter(content_type=project_ct)
        task_permissions = Permission.objects.filter(content_type=task_ct)
        team_permissions = Permission.objects.filter(content_type=team_ct)

        project_manager_group.permissions.add(*project_permissions, *task_permissions, *team_permissions)

        team_member_permissions = [
            Permission.objects.get(codename='view_project', content_type=project_ct),
            Permission.objects.get(codename='add_task', content_type=task_ct),
            Permission.objects.get(codename='change_task', content_type=task_ct),
            Permission.objects.get(codename='view_task', content_type=task_ct),
            Permission.objects.get(codename='view_team', content_type=team_ct),
        ]
        team_member_group.permissions.add(*team_member_permissions)

        self.stdout.write(self.style.SUCCESS('Successfully created groups and permissions'))
