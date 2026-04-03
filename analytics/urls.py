from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('reports/', views.ReportListView.as_view(), name='reports'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/<int:pk>/download/', views.download_report, name='report_download'),
    path('reports/<int:pk>/delete/', views.delete_report, name='report_delete'),

    # Chart endpoints
    path('charts/task-trends/', views.task_trends_chart, name='task_trends'),
    path('charts/productivity/', views.productivity_chart, name='productivity'),
    path('charts/project-metrics/<int:project_id>/', views.project_metrics, name='project_metrics'),

    # Exports
    path('export/', views.export_analytics, name='export'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),

    # Analytics views
    path('user/<int:user_id>/', views.UserAnalyticsView.as_view(), name='user_analytics'),
    path('project/<int:project_id>/', views.ProjectAnalyticsView.as_view(), name='project_analytics'),
    path('team/<int:team_id>/', views.TeamAnalyticsView.as_view(), name='team_analytics'),

    # API endpoints
    path('api/task-data/', views.api_task_data, name='api_task_data'),
    path('api/project-data/', views.api_project_data, name='api_project_data'),
    path('api/user-activity/', views.api_user_activity, name='api_user_activity'),
]