from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from .models import Project, Technology, ProjectMembership
from .forms import ProjectForm
# Create your tests here.
User = get_user_model()
class ProjectsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='projectowner',
            email='owner@example.com',
            password='testpass123'
        )
        self.tech = Technology.objects.create(
            name='Python',
            category='backend',
            icon='fab fa-python'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='This is a test project',
            created_by=self.user,
            start_date=date.today(),
            deadline=date.today() + timedelta(days=30),
            status='planning',
            priority='medium',
            hours_estimated=100
        )
        ProjectMembership.objects.create(
            project=self.project,
            user=self.user,
            role='owner'
        )

    def test_project_list_view(self):
        response = self.client.get(reverse('projects:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertTemplateUsed(response, 'projects/project_list.html')
    def test_project_detail_view(self):
        response = self.client.get(reverse('projects:detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'This is a test project')
        self.assertTemplateUsed(response, 'projects/project_detail.html')
    def test_project_create_authenticated(self):
        self.client.login(username='projectowner', password='testpass123')
        response = self.client.post(reverse('projects:create'), {
            'name': 'New Project',
            'description': 'New project description',
            'start_date': date.today(),
            'deadline': date.today() + timedelta(days=45),
            'status': 'planning',
            'priority': 'high',
            'hours_estimated': 200,
            'is_public': True,
            'technologies': [self.tech.id]
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name='New Project').exists())

    def test_project_create_unauthenticated(self):
        response = self.client.get(reverse('projects:create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('projects:create')}")

    def test_project_update(self):
        self.client.login(username='projectowner', password='testpass123')

        response = self.client.post(reverse('projects:update', args=[self.project.id]), {
            'name': 'Updated Project Name',
            'description': self.project.description,
            'start_date': self.project.start_date,
            'deadline': self.project.deadline,
            'status': 'active',
            'priority': self.project.priority,
            'hours_estimated': self.project.hours_estimated,
            'is_public': self.project.is_public,
        })

        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project Name')
        self.assertEqual(self.project.status, 'active')

    def test_project_delete_with_confirmation(self):
        self.client.login(username='projectowner', password='testpass123')
        response = self.client.get(reverse('projects:delete', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_confirm_delete.html')
        response = self.client.post(reverse('projects:delete', args=[self.project.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())
    def test_project_form_validation(self):
        form = ProjectForm(data={
            'name': 'Test',
            'description': 'Description',
            'start_date': date.today(),
            'deadline': date.today() - timedelta(days=1),
            'status': 'planning',
            'priority': 'medium',
            'hours_estimated': -10,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('deadline', form.errors)
        self.assertIn('hours_estimated', form.errors)

    def test_project_filtering(self):
        Project.objects.create(
            name='Completed Project',
            description='Completed project',
            created_by=self.user,
            start_date=date.today() - timedelta(days=60),
            deadline=date.today() - timedelta(days=30),
            status='completed',
            priority='low'
        )
        response = self.client.get(reverse('projects:list'), {'status': 'completed'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed Project')
        self.assertNotContains(response, 'Test Project')
        response = self.client.get(reverse('projects:list'), {'search': 'Completed'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed Project')

    def test_join_project(self):
        new_user = User.objects.create_user(
            username='newmember',
            email='new@example.com',
            password='testpass123'
        )
        self.client.login(username='newmember', password='testpass123')
        response = self.client.post(reverse('projects:join', args=[self.project.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.project.members.filter(id=new_user.id).exists())




