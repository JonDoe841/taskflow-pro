from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [

    path('', views.TaskListView.as_view(), name='list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='detail'),
    path('create/', views.TaskCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),

    path('my-tasks/', views.MyTasksView.as_view(), name='my_tasks'),

    path('<int:pk>/assign/', views.assign_task, name='assign'),
    path('<int:pk>/change-status/', views.change_task_status, name='change_status'),
    path('<int:pk>/add-comment/', views.add_task_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    path('<int:pk>/add-dependency/<int:dependency_id>/', views.add_dependency, name='add_dependency'),
    path('<int:pk>/remove-dependency/<int:dependency_id>/', views.remove_dependency, name='remove_dependency'),

    path('<int:pk>/subtasks/', views.SubtaskListView.as_view(), name='subtasks'),
    path('<int:pk>/subtasks/create/', views.SubtaskCreateView.as_view(), name='create_subtask'),

    path('bulk-update/', views.bulk_update_tasks, name='bulk_update'),
    path('bulk-delete/', views.bulk_delete_tasks, name='bulk_delete'),

    path('export/', views.export_tasks, name='export'),
]