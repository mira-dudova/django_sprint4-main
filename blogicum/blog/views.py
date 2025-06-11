from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.core.paginator import Paginator

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import (
    PostForm,
    CommentForm,
    RegistrationForm,
    EditProfileForm,
)


class IndexView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(
                pub_date__lte=now(),
                is_published=True,
                category__is_published=True,
            )
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        self.category = get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True,
        )
        return (
            Post.objects.filter(
                pub_date__lte=now(),
                is_published=True,
                category=self.category,
            )
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.prefetch_related('author').all()
        context['form'] = CommentForm()
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get(self.pk_url_kwarg))
        if self.request.user == post.author:
            return post
        queryset = (
            Post.objects.filter(
                pub_date__lte=now(),
                is_published=True,
                category__is_published=True,
            )
            .annotate(comment_count=Count('comments'))
        )
        return get_object_or_404(
            queryset,
            pk=self.kwargs.get(self.pk_url_kwarg)
        )


def registration(request):
    template_name = 'registration/registration_form.html'
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('blog:index')
    return render(request, template_name, {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)

    if request.user == user:
        posts = (
            Post.objects.filter(author=user)
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )
    else:
        posts = (
            Post.objects.filter(author=user, is_published=True)
            .order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request, 'blog/profile.html',
        {'profile': user, 'page_obj': page_obj}
    )


@login_required
def edit_profile(request):
    template_name = 'blog/user.html'
    form = EditProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(
            'blog:profile',
            username=request.user.username
        )
    return render(request, template_name, {'form': form})


class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    model = User
    form_class = EditProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


@login_required
def create_post(request):
    template_name = 'blog/create.html'
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, template_name, {'form': form})


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


@login_required
def post_edit(request, post_id):
    template_name = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.pk)
    return render(request, template_name, {'form': form})


@login_required
def comments_post(request, post_id):
    template_name = 'blog/comment.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all().order_by('created_at')
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id=post.pk)
    return render(
        request,
        template_name,
        {'form': form, 'post': post, 'comments': comments}
    )


@login_required
def comment_edit(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    form = CommentForm(
        request.POST or None, request.FILES or None, instance=comment
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request,
        template_name,
        {'form': form, 'post': comment.post, 'comment': comment}
    )


@login_required
def post_delete(request, post_id):
    template_name = 'blog/create.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(
        request,
        template_name,
        {'form': post, 'is_deleting': True}
    )


@login_required
def comment_delete(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request,
        template_name,
        {'comment': comment, 'is_deleting': True, 'form': None}
    )
