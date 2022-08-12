from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group


User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = self.client
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class PostsURLTests(TestCase):
    """Тесты проверки urls.py для приложения posts"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='user')
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """Проверка корректности использования шаблонов"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{self.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_page_with_author(self):
        """Страница редактирования поста доступная автору."""
        response = self.authorized_author.get(
            f'/posts/{self.post.id}/edit', follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_index_available_to_everyone(self):
        """Главная страница доступна неавторизованному пользователю."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_available_to_everyone(self):
        """Страница групп доступна неавторизованному пользователю."""
        response = self.client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_available_to_everyone(self):
        """Страница профайла доступна неавторизованному пользователю."""
        response = self.client.get(f'/profile/{self.author}/')
        self.assertEqual(response.status_code, 200)

    def test_post_id_available_to_author(self):
        """Страница поста доступна автору"""
        response = self.authorized_author.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_create_available_to_authorized_user(self):
        """Страница создания поста доступна авторизованному пользователю."""
        response = self.authorized_user.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_redirect_create(self):
        """
        Перенаправление неавторизованного пользователя на страницу логина.
        """
        response = self.client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_redirect_post_edit(self):
        """
        Перенаправление неавторизованного пользователя на страницу логина.
        """
        response = self.client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_redirect_post_edit_no_author(self):
        """Перенаправление не автора."""
        response = self.client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )
