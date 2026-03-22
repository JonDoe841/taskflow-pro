from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.


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

#Custom errors
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
def handler403(request, exception):
    return render(request, '403.html', status=403)
def handler400(request, exception):
    return render(request, '400.html', status=400)
def csrf_failure(request, reason=""):
    context = {'reason': reason}
    return render(request, '403.html', context=context, status=403)






