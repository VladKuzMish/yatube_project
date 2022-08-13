import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_user_publish_posts(self):
        """Авторизованный пользователь может публиковать посты."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(('posts:profile'), kwargs={
            'username': f'{self.user.username}'
        }))

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.first())
        self.assertTrue(Post.objects.all, form_data)

    def test_cant_create_post_without_text(self):
        """Тест на проверку невозможности создать пустой пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': '',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый отредактированный текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(('posts:post_edit'), kwargs={
                'post_id': f'{self.post.id}'
            }),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(('posts:post_detail'), kwargs={
            'post_id': f'{self.post.id}',
        }))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text='Тестовый отредактированный текст',
                group=f'{self.group.id}',
            ).exists()
        )

    def test_cant_edit_post_without_text(self):
        """Тест на проверку невозможности редактирвоания пустого поста."""
        posts_count = Post.objects.count()
        form_data = {
            'text': '',
        }
        response = self.authorized_client.post(
            reverse(('posts:post_edit'), kwargs={
                'post_id': f'{self.post.id}'
            }),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_text_label(self):
        title_label = self.form.fields['text'].label
        self.assertEquals(title_label, 'Текст')

    def test_group_label(self):
        title_label = self.form.fields['group'].label
        self.assertEquals(title_label, 'Группа')
