from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Task, TaskComment, TaskTag
from projects.models import Project

# Create your tests here.
User = get_user_model()


class TasksTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='testpass123'
        )
        self.assignee = User.objects.create_user(
            username='assignee',
            email='assignee@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.owner,
            start_date=timezone.now().date(),
            deadline=timezone.now().date() + timedelta(days=30)
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Task Description',
            project=self.project,
            created_by=self.owner,
            assigned_to=self.assignee,
            due_date=timezone.now() + timedelta(days=7),
            estimated_hours=8,
            status='todo'
        )
        self.tag = TaskTag.objects.create(name='bug', color='#ff0000')
        self.task.tags.add(self.tag)

    def test_task_list_view(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(reverse('tasks:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
        self.assertTemplateUsed(response, 'tasks/task_list.html')

    def test_task_detail_view(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(reverse('tasks:detail', args=[self.task.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')
        self.assertContains(response, 'Test Task Description')

    def test_task_create(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('tasks:create'), {
            'title': 'New Task',
            'description': 'New Description',
            'project': self.project.id,
            'assigned_to': self.assignee.id,
            'due_date': (timezone.now() + timedelta(days=5)).isoformat(),
            'estimated_hours': 4,
            'status': 'todo',
            'priority': 'high',
            'tags': [self.tag.id]
        })
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='New Task')
        self.assertIn(self.tag, task.tags.all())
    def test_task_status_transition(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(
            reverse('tasks:change_status', args=[self.task.id]),
            {'status': 'in_progress'}
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')
        self.assertIsNone(self.task.completed_at)
        response = self.client.post(
            reverse('tasks:change_status', args=[self.task.id]),
            {'status': 'done'}
        )

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'done')
        self.assertIsNotNone(self.task.completed_at)

    def test_task_comment(self):
        self.client.login(username='assignee', password='testpass123')
        response = self.client.post(
            reverse('tasks:add_comment', args=[self.task.id]),
            {'content': 'This is a test comment'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TaskComment.objects.filter(
            task=self.task,
            author=self.assignee,
            content='This is a test comment'
        ).exists())
    def test_task_filtering(self):
        self.client.login(username='owner', password='testpass123')
        Task.objects.create(
            title='Completed Task',
            description='Done',
            project=self.project,
            created_by=self.owner,
            due_date=timezone.now() + timedelta(days=3),
            status='done'
        )

        response = self.client.get(reverse('tasks:list'), {'status': 'done'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed Task')
        self.assertNotContains(response, 'Test Task')
        response = self.client.get(reverse('tasks:list'), {'assigned_to': self.assignee.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')

    def test_task_permissions(self):
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123'
        )

        self.client.login(username='other', password='testpass123')
        response = self.client.post(
            reverse('tasks:update', args=[self.task.id]),
            {'title': 'Hacked Task'}
        )
        self.assertEqual(response.status_code, 403)
    def test_task_due_date_validation(self):
        self.client.login(username='owner', password='testpass123')
        response = self.client.post(reverse('tasks:create'), {
            'title': 'Past Due Task',
            'description': 'Description',
            'project': self.project.id,
            'due_date': timezone.now() - timedelta(days=1),
            'estimated_hours': 4,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_date',
                             'Due date cannot be in the past.')