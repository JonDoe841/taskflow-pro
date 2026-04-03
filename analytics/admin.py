from django.contrib import admin
from .models import Report


# Register your models here.
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'project', 'generated_by', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('project__name',)
    readonly_fields = ('created_at', 'data')
