from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


COUNT_POSTS_LIMIT_1 = 10
COUNT_POSTS_LIMIT_2 = 3


class StaticURLTests(TestCase):
    '''Класс для тестирования View'''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.another_group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test',
        )
        cls.post = Post.objects.create(
            text='Тестовая пост',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.guest = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.guest)
        self.user = User.objects.get(username='auth')
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_task_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        object = response.context['page_obj'][0]
        self.assertEqual(object, self.post)

    def test_group_list_page_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse(
                        'posts:group_list',
                        kwargs={'slug': self.group.slug})
                        )
                    )
        self.assertEqual(response.context.get('group', self.group))

    def test_profile_page_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse(
                        'posts:profile',
                        kwargs={'username': self.post.author})
                        )
                    )
        self.assertEqual(response.context.get('author', self.user))

    def test_post_detail_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse(
                        'posts:post_detail',
                        kwargs={'post_id': self.post.id})
                        )
                    )
        self.assertEqual(response.context.get('post', self.post))

    def test_post_create_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse('posts:post_create')))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_post_edit_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse(
                        'posts:post_edit',
                        kwargs={'post_id': self.post.id})
                        )
                    )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)

    def test_additional_verification_when_creating_a_post(self):
        '''Пост появляется на главной странице сайта,
        на странице выбранной группы, в профайле пользователя.'''
        project_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        ]
        for address in project_pages:
            with self.subTest(adress=address):
                response = self.author_client.get(address)
                self.assertEqual(
                    response.context.get('page_obj')[0], self.post
                )

    def test_the_post_was_not_included_in_the_group(self):
        '''Если при создании поста указать группу,
        проверяем, что этот пост не попал в группу,
        для которой не был предназначен.'''
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                args=[self.another_group.slug]
            )
        )
        self.assertNotIn(self.post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    '''Класс для тестирования пагинатора'''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug',
        )
        for i in range(13):
            Post.objects.create(
                text=f'{i} тестовый текст',
                group=cls.group,
                author=cls.user,
            )

    def setUp(self):
        self.client = Client()

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            COUNT_POSTS_LIMIT_1
        )

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            COUNT_POSTS_LIMIT_2
        )
