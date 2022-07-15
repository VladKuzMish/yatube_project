from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            title='Тестовый заголовок',
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """
        Проверяем доступность страницы -
        '/'
        для любого пользователя.
        """
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_post_group_url_exists_at_desired_location(self):
        """
        Проверяем доступность страницы -
        '/group/<slug>/'
        для любого пользователя.
        """
        response = self.guest_client.get('/group/<slug>/')
        self.assertEqual(response.status_code, 200)

    def test_post_profile_url_exists_at_desired_location(self):
        """
        Проверяем доступность страницы -
        '/profile/<username>/'
        для любого пользователя.
        """
        response = self.guest_client.get('/profile/<username>/')
        self.assertEqual(response.status_code, 200)

    def test_posts_id_url_exists_at_desired_location(self):
        """
        Проверяем доступность страницы -
        '/posts/<posts_id>/'
        для любого пользователя.
        """
        response = self.guest_client.get('/posts/<posts_id>/')
        self.assertEqual(response.status_code, 200)

    def test_create_url_exists_at_desired_location(self):
        """
        Проверяем доступность страницы -
        '/create/'
        для авторизованного пользователя.
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_404_url_exists_at_desired_location(self):
        """
        Проверяем наличие ошибки
        404
        при обращении к несуществующей странице.
        """
        response = self.guest_client.get('/group/yaueduzhitvlondon/')
        self.assertEqual(response.status_code, 404)

    def test_edit_url_for_author_exists(self):
        """
        Проверяем, что страница
        редактирования поста
        доступна только для автора поста.
        """
        testing_url = '/posts/1/edit/'
        response = self.post_author.get(testing_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """
        Проверяем, что
        URL-адрес использует
        соответствующий шаблон.
        """
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/NoName/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
