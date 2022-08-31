from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Group, Post, Follow, User
from ..contstants import VARIABLE_POSTS, COUNT_POSTS_LIMIT, NAME_USERS


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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)
        self.user = User.objects.get(username='auth')
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='image.gif',
            content=self.image,
            content_type='image/gif',
        )

        cache.clear()

    def test_pages_uses_correct_template(self):
        """Проверка правильности использования шаблонов."""
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
        """Провекра корректности контекста главной страницы"""
        response = self.authorized_client.get(reverse('posts:index'))
        post_object = response.context['page_obj'][0]
        self.assertEqual(post_object, self.post)
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.id, self.post.id)
        self.assertEqual(post_object.author, self.post.author)
        self.assertEqual(post_object.group, self.group)
        self.assertEqual(post_object.image, self.post.image)

    def test_group_posts_page_show_correct_context(self):
        """Провекра корректности контекста страницы с группами"""
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
        self.assertEqual(group_object.image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Провекра корректности контекста страницы профайла."""
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
        self.assertEqual(profile_object.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Провекра корректности контекста страницы конкретного поста"""
        response = (self.authorized_client.
                    get(reverse(
                        'posts:post_detail',
                        kwargs={'post_id': self.post.id})
                        )
                    )
        self.assertEqual(response.context.get('post'), self.post)

    def test_post_create_show_correct_context(self):
        """Провекра корректности контекста создания поста"""
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
        """Провекра корректности контекста редактирования поста"""
        response = (self.authorized_client.
                    get(reverse(
                        'posts:post_edit',
                        kwargs={'post_id': self.post.id})
                        )
                    )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_fields, expected)
                self.assertEqual(
                    response.context.get('post').text, self.post.text
                )
                self.assertTrue(response.context.get('is_edit'))
                self.assertEqual(response.context.get('is_edit'), True)

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

    def test_cach_in_index_page(self):
        """Проверяем кеширование главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        with_cache = response.content

        Post.objects.create(
            group=self.group,
            text='Новый текст, после кэша',
            author=self.user,
        )

        cache.clear()

        response = self.authorized_client.get(reverse('posts:index'))
        after_clearing_the_cache = response.content
        self.assertNotEqual(with_cache,
                            after_clearing_the_cache)


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

            cache.clear()

    def test_first_page_contains_ten_records(self):
        """Провекра пагинатора, первая страница."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            VARIABLE_POSTS
        )

    def test_second_page_contains_three_records(self):
        """Провекра пагинатора, вторая страница."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            COUNT_POSTS_LIMIT
        )

    def test_paginator_group_one(self):
        """Провекра пагинатора на странице групп, первая страница."""
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
        """Провекра пагинатора на странице групп, вторая страница."""
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
        """Провекра пагинатора на странице профайла, первая страница."""
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
        """Провекра пагинатора на странице профайла, вторая страница."""
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': self.user}
        ) + '?page=2')
        self.assertEqual(
            len(
                response.context['page_obj']
            ),
            COUNT_POSTS_LIMIT
        )


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=NAME_USERS[0])
        cls.user = User.objects.create_user(username=NAME_USERS[1])

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.user_client = Client()
        self.user_client.force_login(self.user)

    def test_follow_on_user(self):
        """Проверка подписки на пользователя."""
        count_follow = Follow.objects.count()
        self.user_client.post(
            reverse('posts:profile_follow', kwargs={'username': self.author})
        )
        follow = Follow.objects.all().latest('id')
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow.author_id, self.author.id)
        self.assertEqual(follow.user_id, self.user.id)

    def test_unfollow_on_user(self):
        """Проверка отписки от пользователя."""
        Follow.objects.create(
            user=self.user,
            author=self.author
        )
        count_follow = Follow.objects.count()
        is_follow = Follow.objects.filter(
            user=self.user,
            author=self.author
        ).exists()

        if is_follow:
            self.user_client.post(
                reverse('posts:profile_unfollow',
                        kwargs={'username': self.author})
            )
            self.assertEqual(Follow.objects.count(), count_follow - 1)

        response = self.user_client.post(
            reverse('posts:profile_unfollow', kwargs={'username': self.author})
        )

        self.assertEqual(response.status_code, 302)
