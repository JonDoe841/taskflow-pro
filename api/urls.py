from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="TaskFlow Pro API",
        default_version='v1',
        description="RESTful API for TaskFlow Pro task management platform",
        terms_of_service="https://www.taskflowpro.com/terms/",
        contact=openapi.Contact(email="api@taskflowpro.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'teams', views.TeamViewSet, basename='team')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'reports', views.ReportViewSet, basename='report')

app_name = 'api'

urlpatterns = [

    path('', include(router.urls)),

    path('auth/', include('rest_framework.urls')),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),

    path('dashboard/', views.DashboardAPIView.as_view(), name='api-dashboard'),

    path('statistics/', views.StatisticsAPIView.as_view(), name='api-statistics'),
    path('statistics/project/<int:project_id>/', views.ProjectStatisticsAPIView.as_view(), name='api-project-stats'),
    path('statistics/user/<int:user_id>/', views.UserStatisticsAPIView.as_view(), name='api-user-stats'),

    path('search/', views.SearchAPIView.as_view(), name='api-search'),

    path('notifications/', views.NotificationListView.as_view(), name='api-notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='api-notification-read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='api-notifications-read-all'),

    path('activity/', views.ActivityFeedView.as_view(), name='api-activity'),
    path('activity/user/<int:user_id>/', views.UserActivityView.as_view(), name='api-user-activity'),

    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('docs.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]