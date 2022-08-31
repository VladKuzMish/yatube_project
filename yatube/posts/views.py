from django.shortcuts import render, get_object_or_404

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .utilites.pagination import pagination
from .models import Post, Group, User, Follow
from .forms import CommentForm, PostForm


@cache_page(20)
def index(request):
    """Функция главной страницы."""
    post = Post.objects.all()
    pagination(request, post)
    context = {
        'page_obj': pagination(request, post),
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Функция страницы групп."""
    group = get_object_or_404(Group, slug=slug)
    post = group.posts.all()
    pagination(request, post)
    context = {
        'group': group,
        'page_obj': pagination(request, post),
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Профайл пользователя."""
    author = get_object_or_404(User, username=username)
    post = author.posts.all()
    pagination(request, post)

    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()
    context = {
        'author': author,
        'page_obj': pagination(request, post),
        'following': following,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Функция страницы поста."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Функция страницы создания поста."""
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Функция страницы редактирования поста."""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:post_detail', post_id=post_id)

    return render(request, 'posts/create_post.html', {
        'form': form,
        'is_edit': True,
        'post': post,
    })


@login_required
def add_comment(request, post_id):
    """Функция для создания комментария."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Главная функция подписок."""
    post = Post.objects.filter(author__following__user=request.user)
    pagination(request, post)
    context = {
        'page_obj': pagination(request, post),
    }
    template = 'posts/follow.html'

    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Функция для подписки на автора"""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Функция для отписки от автора"""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()

    return redirect('posts:profile', username=username)
