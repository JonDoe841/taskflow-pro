from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.views.generic import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.models import Group
from .models import User, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, UserEditForm
# Create your views here.

class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Add user to Team Members group by default
        team_members_group, _ = Group.objects.get_or_create(name='Team Members')
        self.object.groups.add(team_members_group)
        messages.success(self.request, 'Registration successful! Please login.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        return reverse_lazy('projects:list')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('core:home')

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out.')
        return super().dispatch(request, *args, **kwargs)

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        context = {
            'profile_user': user,
            'recent_tasks': user.assigned_tasks.all()[:5],
            'recent_projects': user.projects.all()[:5],
        }
        return render(request, 'accounts/profile.html', context)

class UserProfileEditView(LoginRequiredMixin, View):
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

        context = {
            'user_form': user_form,
            'form': profile_form,
        }
        return render(request, 'accounts/edit_profile.html', context)

    def post(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserEditForm(request.POST, request.FILES, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
            return render(request, 'accounts/edit_profile.html', {
                'user_form': user_form,
                'form': profile_form,
            })



