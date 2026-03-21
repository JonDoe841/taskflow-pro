from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views
schema_view = get_schema_view(
    openapi.Info(
        title="TaskFlow Pro API",
        default_version='v1',
        description="API documentation for TaskFlow Pro task management platform",
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
urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardAPIView.as_view(), name='api-dashboard'),
    path('auth/', include('rest_framework.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]