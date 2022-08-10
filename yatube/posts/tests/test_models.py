from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


NUMBER_OF_CHARACTERS = 15


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
            text='Тут появился тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models_correct = {
            self.post: self.post.text[:NUMBER_OF_CHARACTERS],
            PostModelTest.group: PostModelTest.group.title,
        }
        for correct_option, expected_values in models_correct.items():
            with self.subTest(correct_option=correct_option):
                self.assertEqual(correct_option.__str__(), expected_values,
                                 'Ошибка метода _str__ в'
                                 f'модели {type(correct_option).__name__}')
