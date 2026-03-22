from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.contenttypes.models import ContentType
from .models import UserProfile
from .forms import UserRegistrationForm, UserProfileForm
# Create your tests here.

User = get_user_model()

class AccountsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.project_manager_group = Group.objects.create(name='Project Managers')
        self.team_member_group = Group.objects.create(name='Team Members')
    def test_user_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertTrue(self.team_member_group in new_user.groups.all())

    def test_user_registration_invalid_email(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })

        self.assertEqual(response.status_code, 200)  # Form not valid
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')
    def test_user_login(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })

        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertRedirects(response, reverse('projects:dashboard'))

    def test_user_login_invalid(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 200)  # Form not valid
        self.assertContains(response, 'Please enter a correct username and password')

    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'Test User')

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_edit_form_valid(self):
        self.client.login(username='testuser', password='testpass123')
        profile = UserProfile.objects.create(
            user=self.user,
            skills='Python, Django',
            hourly_rate=50.00,
            github_profile='https://github.com/testuser'
        )
        response = self.client.post(reverse('accounts:edit_profile'), {
            'user': self.user.id,
            'skills': 'Python, Django, JavaScript',
            'hourly_rate': 75.00,
            'github_profile': 'https://github.com/testuser-updated',
            'linkedin_profile': 'https://linkedin.com/in/testuser'
        })
        self.assertEqual(response.status_code, 302)
        profile.refresh_from_db()
        self.assertEqual(profile.skills, 'Python, Django, JavaScript')
        self.assertEqual(float(profile.hourly_rate), 75.00)
    def test_profile_form_validation(self):
        form = UserProfileForm(data={
            'user': self.user.id,
            'hourly_rate': -10,
            'github_profile': 'invalid-url',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('hourly_rate', form.errors)
        self.assertIn('github_profile', form.errors)

    def test_user_groups_permissions(self):
        from projects.models import Project

        content_type = ContentType.objects.get_for_model(Project)
        permission = Permission.objects.get(
            codename='add_project',
            content_type=content_type
        )

        self.project_manager_group.permissions.add(permission)
        self.user.groups.add(self.project_manager_group)

        self.assertTrue(self.user.has_perm('projects.add_project'))




