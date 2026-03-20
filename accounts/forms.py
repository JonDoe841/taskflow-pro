from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, UserProfile
import re
from urllib.parse import urlparse

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Choose a username',
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Your first name',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Your last name',
                'class': 'form-control'
            }),
        }
        help_texts = {
            'username': '150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        }
        error_messages = {
            'username': {
                'unique': 'This username is already taken. Please choose another.',
            },
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('Username can only contain letters, numbers, and underscores.')
        return username

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Enter your username',
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
        'class': 'form-control'
    }))
    error_messages = {
        'invalid_login': "Please enter a correct username and password. Note that both fields may be case-sensitive.",
        'inactive': "This account is inactive.",
    }
class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['user', 'skills', 'hourly_rate', 'github_profile', 'linkedin_profile', 'notifications']
        widgets = {
            'skills': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter your skills separated by commas',
                'class': 'form-control'
            }),
            'notifications': forms.HiddenInput(),  # Exclude from rendering
        }
        labels = {
            'user': 'Username',
            'hourly_rate': 'Hourly Rate ($)',
        }
        help_texts = {
            'skills': 'Example: Python, Django, JavaScript, React',
            'hourly_rate': 'Enter your desired hourly rate in USD',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].disabled = True
        self.fields['user'].widget.attrs['readonly'] = True
        self.fields['github_profile'].widget.attrs['placeholder'] = 'https://github.com/username'
        self.fields['linkedin_profile'].widget.attrs['placeholder'] = 'https://linkedin.com/in/username'
    def clean_hourly_rate(self):
        rate = self.cleaned_data.get('hourly_rate')
        if rate and rate < 0:
            raise ValidationError('Hourly rate cannot be negative.')
        if rate and rate > 1000:
            raise ValidationError('Hourly rate seems too high. Please verify.')
        return rate

    def clean_github_profile(self):
        url = self.cleaned_data.get('github_profile')
        if url:
            domain = urlparse(url).netloc
            if domain not in ['github.com', 'www.github.com']:
                raise ValidationError('Please enter a valid GitHub profile URL.')
        return url
