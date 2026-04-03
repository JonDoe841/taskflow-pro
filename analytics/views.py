from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from projects.models import Project
from tasks.models import Task
from .models import Report


class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get user's projects and tasks
        projects = user.projects.all()
        tasks = user.assigned_tasks.all()

        # Statistics
        context['total_projects'] = projects.count()
        context['active_projects'] = projects.filter(status='active').count()
        context['completed_projects'] = projects.filter(status='completed').count()
        context['total_tasks'] = tasks.count()
        context['completed_tasks'] = tasks.filter(status='done').count()
        context['pending_tasks'] = tasks.filter(status__in=['todo', 'in_progress']).count()

        # Completion rate
        if context['total_tasks'] > 0:
            context['completion_rate'] = round((context['completed_tasks'] / context['total_tasks']) * 100, 1)
        else:
            context['completion_rate'] = 0

        # Chart data
        context['status_labels'] = ['To Do', 'In Progress', 'Review', 'Done', 'Blocked']
        context['status_data'] = [
            tasks.filter(status='todo').count(),
            tasks.filter(status='in_progress').count(),
            tasks.filter(status='review').count(),
            tasks.filter(status='done').count(),
            tasks.filter(status='blocked').count(),
        ]

        context['priority_labels'] = ['Low', 'Medium', 'High', 'Urgent']
        context['priority_data'] = [
            tasks.filter(priority='low').count(),
            tasks.filter(priority='medium').count(),
            tasks.filter(priority='high').count(),
            tasks.filter(priority='urgent').count(),
        ]

        # Project progress data
        context['project_labels'] = [p.name[:20] for p in projects[:10]]
        context['project_progress_data'] = [p.progress_percentage for p in projects[:10]]

        # Status counts for pie chart
        context['status_counts'] = {
            'planning': projects.filter(status='planning').count(),
            'active': projects.filter(status='active').count(),
            'on_hold': projects.filter(status='on_hold').count(),
            'completed': projects.filter(status='completed').count(),
            'cancelled': projects.filter(status='cancelled').count(),
        }

        context['status_counts_data'] = list(context['status_counts'].values())
        context['status_labels_pie'] = list(context['status_counts'].keys())

        return context


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'analytics/reports.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return Report.objects.filter(generated_by=self.request.user).order_by('-created_at')


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'analytics/report_detail.html'
    context_object_name = 'report'


class GenerateReportView(LoginRequiredMixin, CreateView):
    model = Report
    fields = ['report_type', 'project', 'period_start', 'period_end']
    template_name = 'analytics/generate_report.html'
    success_url = reverse_lazy('analytics:reports')

    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        messages.success(self.request, 'Report generated successfully!')
        return super().form_valid(form)


def generate_report(request):
    # Simple redirect for now
    messages.info(request, 'Report generation feature coming soon!')
    return redirect('analytics:reports')


def download_report(request, pk):
    messages.info(request, 'Download feature coming soon!')
    return redirect('analytics:report_detail', pk=pk)


def delete_report(request, pk):
    report = Report.objects.get(pk=pk)
    report.delete()
    messages.success(request, 'Report deleted successfully!')
    return redirect('analytics:reports')


# Chart data endpoints (JSON)
def task_trends_chart(request):
    from django.http import JsonResponse
    data = {
        'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'completed': [5, 12, 8, 15],
        'created': [8, 10, 12, 14]
    }
    return JsonResponse(data)


def productivity_chart(request):
    from django.http import JsonResponse
    data = {
        'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        'hours': [4, 6, 5, 7, 4]
    }
    return JsonResponse(data)


def project_metrics(request, project_id):
    from django.http import JsonResponse
    project = Project.objects.get(pk=project_id)
    tasks = project.tasks.all()
    data = {
        'total_tasks': tasks.count(),
        'completed': tasks.filter(status='done').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'todo': tasks.filter(status='todo').count(),
        'progress': project.progress_percentage
    }
    return JsonResponse(data)


def export_analytics(request):
    from django.http import HttpResponse
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="analytics_export.csv"'
    response.write("Metric,Value\n")
    response.write(f"Total Projects,{request.user.projects.count()}\n")
    response.write(f"Total Tasks,{request.user.assigned_tasks.count()}\n")
    return response


def export_csv(request):
    return export_analytics(request)


def export_pdf(request):
    from django.http import HttpResponse
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response


def user_performance(request, user_id):
    from django.http import JsonResponse
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    data = {
        'username': user.username,
        'total_tasks': user.assigned_tasks.count(),
        'completed_tasks': user.assigned_tasks.filter(status='done').count(),
    }
    return JsonResponse(data)


def api_task_data(request):
    from django.http import JsonResponse
    tasks = request.user.assigned_tasks.all()
    data = {
        'total': tasks.count(),
        'by_status': {
            'todo': tasks.filter(status='todo').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'done': tasks.filter(status='done').count()
        }
    }
    return JsonResponse(data)


def api_project_data(request):
    from django.http import JsonResponse
    projects = request.user.projects.all()
    data = {
        'total': projects.count(),
        'by_status': {
            'active': projects.filter(status='active').count(),
            'completed': projects.filter(status='completed').count()
        }
    }
    return JsonResponse(data)


def api_user_activity(request):
    from django.http import JsonResponse
    data = {'recent_activity': []}
    return JsonResponse(data)


# Stubs for other views
class UserAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/user_analytics.html'


class ProjectAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/project_analytics.html'


class TeamAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/team_analytics.html'