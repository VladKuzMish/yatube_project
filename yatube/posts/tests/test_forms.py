import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from ..models import Group, Post, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый комментарий',
            author=cls.author,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_authorized_user_publish_posts(self):
        """Авторизованный пользователь может публиковать посты."""
        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(('posts:profile'), kwargs={
            'username': f'{self.author.username}'
        }))

        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.first()
        self.assertEqual(last_post.author, self.author)
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.id, form_data['group'])
        self.assertEqual(last_post.image, f'posts/{uploaded.name}')

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

    def test_edit_post_for_valid(self):
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
                text=form_data['text'],
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
                'post_id': self.post.id
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

    def test_post_comment(self):
        """Валидная форма создаёт комментарий к посту."""
        form_data = {
            'author': self.author,
            'text': 'Тестовый комментарий',
            'post_id': self.post.id,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                    'post_id': self.post.id
                    }),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.id
        }))
        self.assertTrue(
            Comment.objects.filter(
                author=self.author,
                text='Тестовый комментарий',
                post_id=self.post.id,
            ).exists()
        )
