from django.views.generic import TemplateView

# Create your views here.
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "core/home.html"

class BlogView(TemplateView):
    template_name = "core/blog.html"

class AboutView(TemplateView):
    template_name = "core/about.html"

class ContactView(TemplateView):
    template_name = "core/contact.html"

class PrivacyView(TemplateView):
    template_name = "core/privacy.html"

