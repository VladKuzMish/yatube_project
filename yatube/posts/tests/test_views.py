from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Group, Post
from ..views import VARIABLE_POSTS

User = get_user_model()


COUNT_POSTS_LIMIT = 3


class StaticURLTests(TestCase):
    '''Класс для тестирования View'''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
            text='Тестовый пост',
            group=cls.group,
            author=User.objects.create_user(username='auth'),
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
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post_object = response.context['page_obj'][0]
        self.assertEqual(post_object, self.post)
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.id, self.post.id)
        self.assertEqual(post_object.author, self.post.author)
        self.assertEqual(post_object.group, self.group)

    def test_group_posts_page_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse(
                        'posts:group_list',
                        kwargs={'slug': self.group.slug})
                        )
                    )
        group_object = response.context['page_obj'][0]
        self.assertEqual(response.context.get('group'), self.group)
        self.assertEqual(group_object.text, self.post.text)
        self.assertEqual(group_object.id, self.post.id)
        self.assertEqual(group_object.author, self.post.author)
        self.assertEqual(group_object.group, self.group)

    def test_profile_page_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse(
                        'posts:profile',
                        kwargs={'username': self.post.author})
                        )
                    )
        profile_object = response.context['page_obj'][0]
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(profile_object.text, self.post.text)
        self.assertEqual(profile_object.id, self.post.id)
        self.assertEqual(profile_object.author, self.post.author)
        self.assertEqual(profile_object.group, self.group)

    def test_post_detail_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse(
                        'posts:post_detail',
                        kwargs={'post_id': self.post.id})
                        )
                    )
        self.assertEqual(response.context.get('post'), self.post)

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
                self.assertIn(
                    response.context['page_obj'][0],
                    Post.objects.all()
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
        for i in range(COUNT_POSTS_LIMIT + VARIABLE_POSTS):
            Post.objects.create(
                text=f'{i} тестовый текст',
                group=cls.group,
                author=cls.user,
            )

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            VARIABLE_POSTS
        )

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            COUNT_POSTS_LIMIT
        )

    def test_paginator_group_one(self):
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}
        ))
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            VARIABLE_POSTS
        )

    def test_paginator_group_two(self):
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}
        ) + '?page=2')
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            COUNT_POSTS_LIMIT
        )

    def test_paginator_profile_one(self):
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': self.user}
        ))
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            VARIABLE_POSTS
        )

    def test_paginator_profile_two(self):
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': self.user}
        ) + '?page=2')
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            COUNT_POSTS_LIMIT
        )
