from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CONSTRAINT_VARIABLE = 15


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

    def __str__(self):
        return self.text[:CONSTRAINT_VARIABLE]


class Group(models.Model):
    """Модель для групп."""

    title = models.CharField('Название', max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.title
