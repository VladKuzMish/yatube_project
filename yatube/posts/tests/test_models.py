from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_str = {PostModelTest.post: PostModelTest.post.text[:15],
                      PostModelTest.group: PostModelTest.group.title}
        for model, expected_values in models_str.items():
            with self.subTest(model=model):
                self.assertEqual(model.__str__(), expected_values,
                                 f'Ошибка метода _str__ в'
                                 f' модели {type(model).__name__}')
