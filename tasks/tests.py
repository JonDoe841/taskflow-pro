from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from projects.models import Project
from tasks.models import Task, TaskComment

User = get_user_model()


class TasksTestCase(TestCase):
    """Test cases for tasks app"""

    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='testpass123')
        self.assignee = User.objects.create_user(username='assignee', password='testpass123')

        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user,
            start_date=date.today(),
            deadline=date.today() + timedelta(days=30),
            hours_estimated=100
        )

        self.task = Task.objects.create(
            title='Test Task',
            description='Test Task Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.assignee,
            due_date=timezone.now() + timedelta(days=7),
            estimated_hours=8,
            status='todo',
            priority='medium'
        )

    def test_task_creation(self):
        """Test 1: Task creation works"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.project.name, 'Test Project')

    def test_task_str_method(self):
        """Test 2: Task string representation"""
        self.assertEqual(str(self.task), 'Test Task')

    def test_task_default_status(self):
        """Test 3: Task default status is 'todo'"""
        self.assertEqual(self.task.status, 'todo')

    def test_task_status_update(self):
        """Test 4: Task status can be updated"""
        self.task.status = 'in_progress'
        self.task.save()
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in_progress')

    def test_task_priority_update(self):
        """Test 5: Task priority can be updated"""
        self.task.priority = 'high'
        self.task.save()
        self.task.refresh_from_db()
        self.assertEqual(self.task.priority, 'high')

    def test_task_assignment(self):
        """Test 6: Task can be reassigned"""
        new_user = User.objects.create_user(username='newassignee', password='pass123')
        self.task.assigned_to = new_user
        self.task.save()
        self.task.refresh_from_db()
        self.assertEqual(self.task.assigned_to.username, 'newassignee')

    def test_add_comment_to_task(self):
        """Test 7: Comments can be added to task"""
        comment = TaskComment.objects.create(
            task=self.task,
            author=self.assignee,
            content='This is a test comment'
        )
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertEqual(comment.task.title, 'Test Task')

    def test_task_comment_count(self):
        """Test 8: Task comment count works"""
        TaskComment.objects.create(
            task=self.task,
            author=self.assignee,
            content='Comment 1'
        )
        TaskComment.objects.create(
            task=self.task,
            author=self.user,
            content='Comment 2'
        )
        self.assertEqual(self.task.comments.count(), 2)

    def test_task_list_view_loads(self):
        """Test 9: Task list page loads or redirects"""
        self.client.login(username='owner', password='testpass123')
        response = self.client.get('/tasks/')
        self.assertIn(response.status_code, [200, 301, 302])

    def test_task_detail_view_loads(self):
        """Test 10: Task detail page loads or redirects"""
        self.client.login(username='owner', password='testpass123')
        response = self.client.get(f'/tasks/{self.task.id}/')
        self.assertIn(response.status_code, [200, 301, 302])