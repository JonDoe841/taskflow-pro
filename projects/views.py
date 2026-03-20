from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from .models import Project, ProjectMembership
from .forms import ProjectForm, ProjectMembershipForm
from django.contrib.auth.decorators import login_required
# Create your views here.
class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 9
    def get_queryset(self):
        queryset = Project.objects.all()

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        queryset = queryset.annotate(
            total_tasks=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__status='done'))
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

        context['members'] = project.members.all()[:6]

        if self.request.user.is_authenticated:
            context['is_member'] = project.members.filter(id=self.request.user.id).exists()

        return context

class ProjectCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    permission_required = 'projects.add_project'
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Project created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})

class ProjectUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    permission_required = 'projects.change_project'
    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})

class ProjectDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):

    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('projects:list')
    permission_required = 'projects.delete_project'
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Project deleted successfully!')
        return super().delete(request, *args, **kwargs)

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






