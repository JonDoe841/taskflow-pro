from django.contrib import admin
from .models import Task, TaskTag, TaskComment


# Register your models here.
class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority', 'project')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    inlines = [TaskCommentInline]
    fieldsets = (
        ('Task Info', {'fields': ('title', 'description', 'project')}),
        ('Assignment', {'fields': ('created_by', 'assigned_to')}),
        ('Status', {'fields': ('status', 'priority')}),
        ('Dates', {'fields': ('due_date', 'completed_at')}),
        ('Tracking', {'fields': ('estimated_hours', 'logged_hours')}),
        ('Relationships', {'fields': ('parent_task', 'dependencies', 'tags')}),
    )

@admin.register(TaskTag)
class TaskTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at', 'is_edited')
    list_filter = ('created_at',)
    search_fields = ('content',)


