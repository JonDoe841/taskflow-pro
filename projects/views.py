from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Project, ProjectMembership
from .forms import ProjectForm
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

class ProjectMembersView(APIView):
    def get(self, request, pk):
        return Response({"message": "Project members endpoint"})
class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 9

    def get_queryset(self):
        queryset = Project.objects.all()

        # Filters
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Project.STATUS_CHOICES
        context['priority_choices'] = Project.PRIORITY_CHOICES
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        context['todo_tasks'] = project.tasks.filter(status='todo')[:5]
        context['in_progress_tasks'] = project.tasks.filter(status='in_progress')[:5]
        context['done_tasks'] = project.tasks.filter(status='done')[:5]

        context['memberships'] = project.projectmembership_set.select_related('user').all()[:6]

        if self.request.user.is_authenticated:
            context['is_member'] = project.members.filter(id=self.request.user.id).exists()

        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        ProjectMembership.objects.create(
            project=self.object,
            user=self.request.user,
            role='owner'
        )

        messages.success(self.request, f'Project "{self.object.name}" created successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'

    def test_func(self):
        project = self.get_object()
        return project.created_by == self.request.user

    def form_valid(self, form):
        messages.success(self.request, f'Project "{self.object.name}" updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:list')

    def test_func(self):
        project = self.get_object()
        return project.created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        messages.success(request, f'Project "{project.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ProjectDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['total_projects'] = user.projects.count()
        context['active_projects'] = user.projects.filter(status='active').count()
        context['completed_projects'] = user.projects.filter(status='completed').count()
        context['total_tasks'] = user.assigned_tasks.count()
        context['pending_tasks'] = user.assigned_tasks.filter(status__in=['todo', 'in_progress']).count()

        context['user_projects'] = user.projects.all()[:10]
        context['upcoming_deadlines'] = user.assigned_tasks.filter(
            due_date__gte=timezone.now(),
            status__in=['todo', 'in_progress']
        ).order_by('due_date')[:10]

        return context


@login_required
def join_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    membership, created = ProjectMembership.objects.get_or_create(
        project=project,
        user=request.user,
        defaults={'role': 'developer'}
    )

    if created:
        messages.success(request, f'You have joined project "{project.name}"!')
    else:
        messages.info(request, 'You are already a member of this project.')

    return redirect('projects:detail', pk=pk)


@login_required
def leave_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    membership = ProjectMembership.objects.filter(project=project, user=request.user)

    if membership.exists():
        membership.delete()
        messages.success(request, f'You have left project "{project.name}".')
    else:
        messages.error(request, 'You are not a member of this project.')

    return redirect('projects:list')

def remove_member(request, pk, user_id):
    return JsonResponse({
        "message": f"Remove user {user_id} from project {pk}"
    })
def update_member_role(request, pk, user_id):
    return JsonResponse({
        "message": f"Update role for user {user_id} in project {pk}"
    })
def export_project_data(request, pk):
    return JsonResponse({
        "message": f"Export data for project {pk}"
    })
def generate_project_report(request, pk):
    return JsonResponse({
        "message": f"Generate report for project {pk}"
    })

