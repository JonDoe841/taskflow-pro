from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.ProjectUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='delete'),
    path('dashboard/', views.ProjectDashboardView.as_view(), name='dashboard'),

    path('<int:pk>/join/', views.join_project, name='join'),
    path('<int:pk>/leave/', views.leave_project, name='leave'),

    path('<int:pk>/members/', views.ProjectMembersView.as_view(), name='members'),
    path('<int:pk>/members/remove/<int:user_id>/', views.remove_member, name='remove_member'),
    path('<int:pk>/members/update-role/<int:user_id>/', views.update_member_role, name='update_role'),

    path('<int:pk>/export/', views.export_project_data, name='export'),
    path('<int:pk>/generate-report/', views.generate_project_report, name='generate_report'),
]