from django.contrib import admin
from .models import Team, TeamMembership

# Register your models here.

class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 1

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'lead', 'created_by', 'member_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    inlines = [TeamMembershipInline]
    readonly_fields = ('created_at', 'updated_at')
