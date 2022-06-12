from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Post, Group

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
