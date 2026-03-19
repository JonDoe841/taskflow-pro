from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User, UserProfile
# Create your views here.

class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        from django.contrib.auth.models import Group
        team_members_group = Group.objects.get(name='Team Members')
        self.object.groups.add(team_members_group)
        return response

class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('projects:dashboard')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')

class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    def get_object(self):
        return self.request.user

class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/edit_profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['user'].disabled = True
        return form