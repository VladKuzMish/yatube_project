from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel
from .contstants import CONSTRAINT_VARIABLE

User = get_user_model()


class Post(models.Model):
    """Модель для постов."""

    text = models.TextField(max_length=800)
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        'Group',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:CONSTRAINT_VARIABLE]


class Group(models.Model):
    """Модель для групп."""

    title = models.CharField('Название', max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.title


class Comment(CreatedModel):
    """Модель для создания комментариев."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(max_length=500)

    class Meta:
        ordering = ('created',)


class Follow(models.Model):
    """Модель для подписки на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow')]
        verbose_name = 'Подписка',
        verbose_name_plural = 'Подписки'
