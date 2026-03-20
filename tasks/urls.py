from django.urls import path
from django.views.generic import TemplateView

app_name = 'tasks'

urlpatterns = [
    path('', TemplateView.as_view(template_name='tasks/list.html'), name='list'),
]



