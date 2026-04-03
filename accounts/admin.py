from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile

# Register your models here.
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'department', 'is_active')
    list_filter = ('is_active', 'is_staff', 'department')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'avatar', 'phone_number', 'department', 'position', 'date_joined_company', 'is_available')}),
    )

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'hourly_rate', 'github_profile')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

