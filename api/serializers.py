from django.utils import timezone
from rest_framework import serializers

from analytics.models import Report
from projects.models import Project, Technology
from tasks.models import Task, TaskComment, TaskTag
from accounts.models import User, UserProfile
from teams.models import Team


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name',
            'full_name', 'avatar',
            'department', 'position', 'is_available'
        ]
class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ['id', 'name', 'category', 'icon']
class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    technologies = TechnologySerializer(many=True, read_only=True)
    task_count = serializers.IntegerField(read_only=True)
    progress = serializers.FloatField(source='progress_percentage', read_only=True)
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description',
            'created_by', 'technologies',
            'task_count', 'progress',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=TaskTag.objects.all()
    )
    comment_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'completed_at']
    def validate_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past")
        return value
class TaskCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    class Meta:
        model = TaskComment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    members = serializers.SerializerMethodField()
    technologies = TechnologySerializer(many=True, read_only=True)
    recent_tasks = serializers.SerializerMethodField()
    task_stats = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description',
            'created_by',
            'members',
            'technologies',
            'recent_tasks',
            'task_stats',
            'created_at', 'updated_at'
        ]

    def get_members(self, obj):
        memberships = obj.projectmembership_set.select_related('user').all()
        return [
            {
                'user': UserSerializer(m.user, context=self.context).data,
                'role': m.role,
                'joined_at': m.joined_at,
                'contribution_hours': m.contribution_hours,
            }
            for m in memberships
        ]

    def get_recent_tasks(self, obj):
        recent_tasks = (
            obj.tasks
            .select_related('assigned_to', 'created_by')
            .prefetch_related('tags')
            .order_by('-created_at')[:5]
        )
        return TaskSerializer(recent_tasks, many=True, context=self.context).data

    def get_task_stats(self, obj):
        from django.db.models import Count, Q

        return obj.tasks.aggregate(
            total=Count('id'),
            todo=Count('id', filter=Q(status='todo')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            review=Count('id', filter=Q(status='review')),
            done=Count('id', filter=Q(status='done')),
            blocked=Count('id', filter=Q(status='blocked')),
        )
class TeamSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'members', 'projects', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
CommentSerializer = TaskCommentSerializer
