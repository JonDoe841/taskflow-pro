from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Task, TaskComment
from .forms import TaskForm, TaskCommentForm
from django.http import JsonResponse
# Create your views here.
class SubtaskListView(LoginRequiredMixin, View):
    def get(self, request, pk):
        return JsonResponse({"message": f"List subtasks for task {pk}"})


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 15

    def get_queryset(self):
        # Show tasks where user is either:
        # 1. The creator
        # 2. The assignee
        # 3. Part of the project team
        queryset = Task.objects.filter(
            Q(created_by=self.request.user) |
            Q(assigned_to=self.request.user) |
            Q(project__members=self.request.user)
        ).distinct()

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        # Order by due date (soonest first)
        queryset = queryset.order_by('due_date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context



class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'

    def get_initial(self):
        initial = super().get_initial()
        project_id = self.request.GET.get('project')
        if project_id:
            initial['project'] = project_id
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Task "{self.object.title}" created successfully!')
        return response

    def get_success_url(self):
        return reverse_lazy('tasks:detail', kwargs={'pk': self.object.pk})


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'

    def test_func(self):
        task = self.get_object()
        return task.created_by == self.request.user or task.assigned_to == self.request.user

    def form_valid(self, form):
        messages.success(self.request, f'Task "{self.object.title}" updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tasks:detail', kwargs={'pk': self.object.pk})


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')

    def test_func(self):
        task = self.get_object()
        return task.created_by == self.request.user

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        messages.success(request, f'Task "{task.title}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


class MyTasksView(LoginRequiredMixin, TemplateView):
    template_name = 'tasks/my_tasks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        all_tasks = user.assigned_tasks.all()

        context['total_tasks'] = all_tasks.count()
        context['in_progress_tasks'] = all_tasks.filter(status='in_progress').count()
        context['completed_tasks'] = all_tasks.filter(status='done').count()
        context['overdue_tasks'] = all_tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        ).count()

        context['pending_tasks'] = all_tasks.filter(status='todo')
        context['in_progress_tasks_list'] = all_tasks.filter(status='in_progress')
        context['completed_tasks_list'] = all_tasks.filter(status='done')
        context['overdue_tasks_list'] = all_tasks.filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        )

        return context


@login_required
def change_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    new_status = request.POST.get('status')

    if new_status in dict(Task.STATUS_CHOICES):
        task.status = new_status
        task.save()
        messages.success(request, f'Task status updated to {task.get_status_display()}')

    return redirect('tasks:detail', pk=pk)


@login_required
def add_task_comment(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            TaskComment.objects.create(
                task=task,
                author=request.user,
                content=content
            )
            messages.success(request, 'Comment added successfully!')

    return redirect('tasks:detail', pk=pk)

def assign_task(request, pk):
    return JsonResponse({
        "message": f"Assign task {pk}"
    })
def edit_comment(request, comment_id):
    return JsonResponse({
        "message": f"Edit comment {comment_id}"
    })
def delete_comment(request, comment_id):
    return JsonResponse({
        "message": f"Delete comment {comment_id}"
    })
def add_dependency(request, pk, dependency_id):
    return JsonResponse({
        "message": f"Add dependency {dependency_id} to task {pk}"
    })
def remove_dependency(request, pk, dependency_id):
    return JsonResponse({
        "message": f"Remove dependency {dependency_id} from task {pk}"
    })
class SubtaskCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        return JsonResponse({"message": f"Create subtask for task {pk}"})


@login_required
def bulk_update_tasks(request):
    return JsonResponse({"message": "Bulk update tasks"})

@login_required
def bulk_delete_tasks(request):
    return JsonResponse({"message": "Bulk delete tasks"})

# Export tasks
@login_required
def export_tasks(request):
    return JsonResponse({"message": "Export tasks"})
