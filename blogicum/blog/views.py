from datetime import datetime

from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView)

from blog.forms import PostForm, CommentForm
from blog.models import Post, Category, User, Comment


class RegistrationView(LoginRequiredMixin, CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm

    def success_url(self,):
        return self.request.META.get('HTTP_REFERER')


class UserProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_LIMIT

    def get_queryset(self):
        profile = User.objects.get(username=self.kwargs['username'])
        return profile.posts.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = User.objects.get(username=self.kwargs['username'])
        context['profile'] = profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'blog/user_form.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy('blog:profile', kwargs={'username': username})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            return None
        return obj

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj is None:
            return redirect(reverse(
                'blog:post_detail',
                kwargs={'post_id': self.kwargs['post_id']}))
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.author != request.user:
            return redirect(self.success_url)
        return super().post(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    login_url = '/login/'

    def form_valid(self, form):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse('blog:post_detail', kwargs={'post_id': post_id})

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']
        comment_id = self.kwargs['comment_id']
        queryset = self.get_queryset()
        queryset = queryset.filter(post_id=post_id, id=comment_id)
        return get_object_or_404(queryset)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:post_detail')

    def get_object(self, queryset=None):
        post_id = self.kwargs['post_id']
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, id=comment_id, post_id=post_id)

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = settings.POSTS_LIMIT

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.make_aware(datetime.now()),
        ).order_by('-pub_date')
        queryset = queryset.annotate(comment_count=Count('comments'))
        return queryset


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = settings.POSTS_LIMIT

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug,
                                     is_published=True)
        queryset = queryset.filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now())
        queryset = queryset.prefetch_related('comments')
        queryset = queryset.order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = context['post_list']
        comment_counts = []
        for post in posts:
            comment_counts.append(post.comments.count())
        context['comment_counts'] = comment_counts
        return context
