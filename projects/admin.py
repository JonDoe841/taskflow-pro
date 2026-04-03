from django.contrib import admin
from .models import Project, Technology, ProjectMembership

class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'priority', 'created_by', 'deadline', 'progress_percentage')
    list_filter = ('status', 'priority', 'technologies')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'hours_logged')
    inlines = [ProjectMembershipInline]

    fieldsets = (
        ('Basic Information', {'fields': ('name', 'description', 'created_by')}),
        ('Timeline', {'fields': ('start_date', 'deadline', 'completed_date')}),
        ('Status', {'fields': ('status', 'priority')}),
        ('Metrics', {'fields': ('budget', 'hours_estimated', 'hours_logged')}),
        ('Team', {'fields': ('team',)}),
        ('Settings', {'fields': ('is_public', 'technologies')}),
    )

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon')
    search_fields = ('name',)

