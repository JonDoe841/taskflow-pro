from django.db.models import Q  # ← CHANGED THIS LINE
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import BlogPost, BlogComment
from .forms import BlogCommentForm

# Create your views here.


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = BlogPost.objects.filter(is_published=True)[:3]
        return context


class ContactView(TemplateView):
    template_name = 'core/contact.html'

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        try:
            send_mail(
                f'Contact Form: {subject}',
                f'From: {name} <{email}>\n\n{message}',
                email,
                [settings.DEFAULT_FROM_EMAIL or 'admin@taskflowpro.com'],
                fail_silently=False,
            )
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
        except Exception:
            messages.error(request, 'There was an error sending your message. Please try again later.')

        return redirect('core:contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BlogListView(ListView):
    model = BlogPost
    template_name = 'core/blog.html'
    context_object_name = 'blog_posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True).order_by('-published_date')

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = BlogPost.objects.filter(is_published=True).values_list('category', flat=True).distinct()
        return context


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'core/blog_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.get_object().comments.filter(is_approved=True)
        context['comment_form'] = BlogCommentForm()
        return context


class BlogCommentView(LoginRequiredMixin, CreateView):
    model = BlogComment
    form_class = BlogCommentForm
    http_method_names = ['post']

    def form_valid(self, form):
        post = get_object_or_404(BlogPost, slug=self.kwargs['slug'])
        form.instance.post = post
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Your comment has been posted!')
        return response

    def get_success_url(self):
        return reverse_lazy('core:blog_detail', kwargs={'slug': self.kwargs['slug']})


def handler400(request, exception):
    return render(request, '400.html', status=400)


def handler403(request, exception):
    return render(request, '403.html', status=403)


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


import traceback
from django.http import HttpResponse


def debug_blog(request):
    try:
        from core.models import BlogPost
        posts = BlogPost.objects.filter(is_published=True)

        # Try to render the template
        from django.template import loader
        template = loader.get_template('core/blog.html')

        # Try to get context
        context = {
            'blog_posts': posts,
            'categories': BlogPost.objects.filter(is_published=True).values_list('category', flat=True).distinct()
        }

        return HttpResponse(f"""
        <h1>Debug Info</h1>
        <p>Blog posts found: {posts.count()}</p>
        <p>Template loaded: core/blog.html</p>
        <p>Categories: {list(context['categories'])}</p>
        """)
    except Exception as e:
        return HttpResponse(f"<pre>Error: {str(e)}\n\n{traceback.format_exc()}</pre>")