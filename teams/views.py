from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from .models import Team, TeamMembership
from .forms import TeamForm


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = 'teams/team_list.html'
    context_object_name = 'teams'

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = 'teams/team_detail.html'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['memberships'] = self.get_object().team_memberships.all()
        return context


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = 'teams/team_form.html'
    success_url = reverse_lazy('teams:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        # Add creator as team lead
        TeamMembership.objects.create(
            team=self.object,
            user=self.request.user,
            role='lead'
        )
        messages.success(self.request, f'Team "{self.object.name}" created successfully!')
        return response


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = 'teams/team_form.html'
    success_url = reverse_lazy('teams:list')

    def form_valid(self, form):
        messages.success(self.request, f'Team "{self.object.name}" updated successfully!')
        return super().form_valid(form)


class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    template_name = 'teams/team_confirm_delete.html'
    success_url = reverse_lazy('teams:list')

    def delete(self, request, *args, **kwargs):
        team = self.get_object()
        messages.success(request, f'Team "{team.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)