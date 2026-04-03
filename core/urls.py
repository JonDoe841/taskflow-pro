from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('privacy/', TemplateView.as_view(template_name='core/privacy.html'), name='privacy'),

    # Blog
    path('blog/', views.BlogListView.as_view(), name='blog'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<slug:slug>/comment/', views.BlogCommentView.as_view(), name='blog_comment'),
    path('debug-blog/', views.debug_blog, name='debug_blog'),path('debug-blog/', views.debug_blog, name='debug_blog'),
]