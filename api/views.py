from django.contrib.auth import get_user_model
from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView

from projects.models import Project
from tasks.models import Task
# Placeholder serializers for imports to work
from .serializers import UserSerializer, ProjectSerializer, TaskSerializer, CommentSerializer, TeamSerializer, ReportSerializer
User = get_user_model()

class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        projects = user.projects.all()
        tasks = user.assigned_tasks.all()

        data = {
            'projects_count': projects.count(),
            'active_projects': projects.filter(status='active').count(),
            'tasks_count': tasks.count(),
            'pending_tasks': tasks.filter(status__in=['todo', 'in_progress']).count(),
            'completed_tasks': tasks.filter(status='done').count(),
            'recent_tasks': TaskSerializer(tasks[:5], many=True).data,
            'recent_projects': ProjectSerializer(projects[:5], many=True).data,
        }

        return Response(data)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = []
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]

class CommentViewSet(viewsets.ModelViewSet):
    queryset = []
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

class ReportViewSet(viewsets.ModelViewSet):
    queryset = []
    serializer_class = ReportSerializer
    permission_classes = [permissions.AllowAny]

class StatisticsAPIView(views.APIView):
    def get(self, request):
        return Response({"detail": "Statistics placeholder"})

class ProjectStatisticsAPIView(views.APIView):
    def get(self, request, project_id):
        return Response({"project_id": project_id})

class UserStatisticsAPIView(views.APIView):
    def get(self, request, user_id):
        return Response({"user_id": user_id})

class SearchAPIView(views.APIView):
    def get(self, request):
        return Response({"results": []})

class NotificationListView(views.APIView):
    def get(self, request):
        return Response({"notifications": []})

def mark_notification_read(request, pk):
    return Response({"detail": f"Marked {pk} as read"})

def mark_all_notifications_read(request):
    return Response({"detail": "All notifications marked as read"})

class ActivityFeedView(views.APIView):
    def get(self, request):
        return Response({"activity": []})

class UserActivityView(views.APIView):
    def get(self, request, user_id):
        return Response({"user_id": user_id, "activity": []})
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]