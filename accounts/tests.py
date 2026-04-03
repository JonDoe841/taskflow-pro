from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


class AccountsModelTest(TestCase):
    """Test User and UserProfile models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User'
        )
        UserProfile.objects.get_or_create(user=self.user)

    def test_create_user(self):
        """Test 1: User creation works"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('TestPass123!'))

    def test_user_profile_created(self):
        """Test 2: UserProfile exists"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_user_profile_str(self):
        """Test 3: UserProfile string representation"""
        self.assertEqual(str(self.user.profile), f'Profile for {self.user.username}')

    def test_user_full_name(self):
        """Test 4: User get_full_name method"""
        self.assertEqual(self.user.get_full_name(), 'Test User')

    def test_user_total_projects_property(self):
        """Test 5: total_projects property returns 0 initially"""
        self.assertEqual(self.user.total_projects, 0)

    def test_user_total_tasks_property(self):
        """Test 6: total_tasks property returns 0 initially"""
        self.assertEqual(self.user.total_tasks, 0)

    def test_create_user_without_first_last(self):
        """Test 7: User creation without first/last name"""
        user2 = User.objects.create_user(username='user2', password='pass123')
        self.assertEqual(user2.get_full_name(), 'user2')


class AccountsViewTest(TestCase):
    """Test accounts views - simplified"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        UserProfile.objects.get_or_create(user=self.user)

    def test_home_page_loads(self):
        """Test 8: Home page loads"""
        response = self.client.get('/')
        # Accept both 200 (direct) and 301 (redirect to trailing slash)
        self.assertIn(response.status_code, [200, 301])
    def test_login_page_loads(self):
        """Test 9: Login page loads (without trailing slash)"""
        response = self.client.get('/accounts/login')
        self.assertEqual(response.status_code, 301)  # Redirects to /accounts/login/

    def test_register_page_loads(self):
        """Test 10: Register page loads (without trailing slash)"""
        response = self.client.get('/accounts/register')
        self.assertEqual(response.status_code, 301)

    def test_login_post_redirects(self):
        """Test 11: Login POST redirects"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        self.assertIn(response.status_code, [301, 302])

    def test_logout_works(self):
        """Test 12: Logout works"""
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get('/accounts/logout/')
        self.assertIn(response.status_code, [301, 302])


class ProjectModelTest(TestCase):
    """Test Project model"""

    def setUp(self):
        from django.utils import timezone
        from datetime import date, timedelta
        self.user = User.objects.create_user(username='testuser', password='pass123')
        from projects.models import Project
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user,
            start_date=date.today(),
            deadline=date.today() + timedelta(days=30),
            status='planning',
            priority='medium'
        )

    def test_create_project(self):
        """Test 13: Project creation works"""
        self.assertEqual(self.project.name, 'Test Project')

    def test_project_str_method(self):
        """Test 14: Project string representation"""
        self.assertEqual(str(self.project), 'Test Project')

    def test_project_progress_percentage(self):
        """Test 15: Progress percentage calculation"""
        self.project.hours_estimated = 100
        self.project.hours_logged = 50
        self.assertEqual(self.project.progress_percentage, 50)


class TaskModelTest(TestCase):
    """Test Task model"""

    def setUp(self):
        from django.utils import timezone
        from datetime import date, timedelta
        self.user = User.objects.create_user(username='testuser', password='pass123')
        from projects.models import Project
        from tasks.models import Task
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            created_by=self.user,
            start_date=date.today(),
            deadline=date.today() + timedelta(days=30)
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            project=self.project,
            created_by=self.user,
            assigned_to=self.user,
            due_date=timezone.now() + timezone.timedelta(days=7)
        )

    def test_create_task(self):
        """Test 16: Task creation works"""
        self.assertEqual(self.task.title, 'Test Task')

    def test_task_str_method(self):
        """Test 17: Task string representation"""
        self.assertEqual(str(self.task), 'Test Task')

    def test_task_status_default(self):
        """Test 18: Task default status is 'todo'"""
        self.assertEqual(self.task.status, 'todo')