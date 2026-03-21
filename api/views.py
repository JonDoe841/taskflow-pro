import logging
from datetime import timedelta
from django.db.models import Q, Count, Avg, Sum, F
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from projects.models import Project
from tasks.models import Task, TaskComment
from accounts.models import User
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer, TaskSerializer,
    UserSerializer, TaskCommentSerializer
)
from .permissions import IsProjectMember, IsOwnerOrReadOnly
logger = logging.getLogger(__name__)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Project.objects.all()

        if status_param := self.request.query_params.get('status'):
            queryset = queryset.filter(status=status_param)

        if user_id := self.request.query_params.get('user'):
            queryset = queryset.filter(members__id=user_id)

        if search := self.request.query_params.get('search'):
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        project = self.get_object()

        if project.members.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'Already a member of this project'},
                status=status.HTTP_400_BAD_REQUEST
            )

        project.members.add(request.user)

        from tasks.tasks import send_task_assignment_email
        send_task_assignment_email.delay(
            project.id,
            request.user.email,
            request.user.username
        )
        return Response({'detail': 'Successfully joined the project'})

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        project = self.get_object()
        tasks = project.tasks.select_related('assigned_to', 'created_by').prefetch_related('tags')
        if status_param := request.query_params.get('status'):
            tasks = tasks.filter(status=status_param)

        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = TaskSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(TaskSerializer(tasks, many=True).data)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        project = self.get_object()
        tasks = project.tasks.all()

        total = tasks.count()
        done = tasks.filter(status='done').count()
        stats = {
            'total_tasks': total,
            'tasks_by_status': list(tasks.values('status').annotate(count=Count('id'))),
            'tasks_by_priority': list(tasks.values('priority').annotate(count=Count('id'))),
            'tasks_by_assignee': list(tasks.values('assigned_to__username').annotate(count=Count('id'))),
            'completion_rate': (done / total * 100) if total else 0,
            'total_hours_logged': tasks.aggregate(total=Sum('logged_hours'))['total'] or 0,
            'average_completion_time': tasks.filter(
                status='done',
                completed_at__isnull=False
            ).annotate(
                completion_time=F('completed_at') - F('created_at')
            ).aggregate(avg_time=Avg('completion_time'))['avg_time'],
        }

        return Response(stats)
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMember]
    def get_queryset(self):
        queryset = Task.objects.select_related(
            'project', 'assigned_to', 'created_by'
        ).prefetch_related('tags').annotate(
            comment_count=Count('comments')
        )
        params = self.request.query_params
        if project_id := params.get('project'):
            queryset = queryset.filter(project_id=project_id)
        if assigned_to := params.get('assigned_to'):
            queryset = queryset.filter(assigned_to_id=assigned_to)
        if status_param := params.get('status'):
            queryset = queryset.filter(status=status_param)
        if params.get('due_soon'):
            queryset = queryset.filter(
                due_date__lte=timezone.now() + timedelta(days=7),
                status__in=['todo', 'in_progress']
            )
        return queryset
    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        if task.assigned_to:
            from tasks.tasks import send_task_assignment_email
            send_task_assignment_email.delay(
                task.id,
                task.assigned_to.email,
                self.request.user.username
            )
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        task = self.get_object()
        user_id = request.data.get('user_id')
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({'detail': 'User not found'}, status=404)
        task.assigned_to = user
        task.save(update_fields=['assigned_to'])
        logger.info(f"Task {task.id} assigned to {user.username}")
        return Response({'detail': f'Task assigned to {user.username}'})
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        task = self.get_object()
        serializer = TaskCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save(update_fields=['status'])
            logger.info(
                f"Task {task.id} status changed to {new_status} by {request.user.username}"
            )
            return Response({'detail': f'Status changed to {new_status}'})
        return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        user = self.get_object()
        tasks = user.assigned_tasks.select_related('project')
        if status_param := request.query_params.get('status'):
            tasks = tasks.filter(status=status_param)

        return Response(TaskSerializer(tasks, many=True).data)
    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(self.get_serializer(request.user).data)
class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = request.user
        projects = user.projects.all()
        tasks = user.assigned_tasks.all()
        return Response({
            'projects_count': projects.count(),
            'active_projects': projects.filter(status='active').count(),
            'tasks_count': tasks.count(),
            'pending_tasks': tasks.filter(status__in=['todo', 'in_progress']).count(),
            'completed_tasks': tasks.filter(status='done').count(),
            'tasks_due_soon': tasks.filter(
                due_date__lte=timezone.now() + timedelta(days=3),
                status__in=['todo', 'in_progress']
            ).count(),
            'recent_activities': self.get_recent_activities(user),
            'project_progress': self.get_project_progress(projects),
        })

    def get_recent_activities(self, user):
        recent_tasks = user.assigned_tasks.order_by('-updated_at')[:5]
        recent_comments = TaskComment.objects.filter(author=user).order_by('-created_at')[:5]

        activities = []

        for task in recent_tasks:
            activities.append({
                'type': 'task_update',
                'description': f'Task "{task.title}" was updated',
                'timestamp': task.updated_at,
                'project': task.project.name,
            })

        for comment in recent_comments:
            activities.append({
                'type': 'comment',
                'description': f'Commented on task "{comment.task.title}"',
                'timestamp': comment.created_at,
                'project': comment.task.project.name,
            })

        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:10]

    def get_project_progress(self, projects):
        return [
            {
                'id': project.id,
                'name': project.name,
                'progress': project.progress_percentage,
                'status': project.status,
            }
            for project in projects
        ]



