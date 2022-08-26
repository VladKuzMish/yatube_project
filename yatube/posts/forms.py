from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'text': 'Текст', 'group': 'Группа'}


class CommentAdd(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('post', 'author', 'text')
        labels = {'post': 'Пост', 'author': 'Автор', 'text': 'Текст'}
