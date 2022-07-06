from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import redirect

from .models import Post, Group, User

from .forms import PostForm

VARIABLE_POSTS = 10


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, VARIABLE_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(
        group=group
    ).order_by('-pub_date')[:VARIABLE_POSTS]
    context = {
        'group': group,
        'posts': posts,
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Профайл пользователя."""

    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    posts_count = Post.objects.filter(author=author).count()
    paginator = Paginator(post_list, VARIABLE_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    group = post.group
    author = post.author
    posts_count = author.posts.count()
    context = {
        'post': post,
        'group': group,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
    else:
        form = PostForm()

    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect('post_detail', pk=post.post_id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_edit.html', {'form': form})
