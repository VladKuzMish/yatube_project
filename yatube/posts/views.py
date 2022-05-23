#from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, request


# Главная страница
def index(request):    
    return HttpResponse('Главная страница')


# Страница c постами
def group_posts(request, slug):
    return HttpResponse('Пост')
