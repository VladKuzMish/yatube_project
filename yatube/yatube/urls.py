from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
]
