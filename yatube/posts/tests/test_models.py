from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostGroupModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username="authorized_user",
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Это текст для тестирования модели, а его длина точно >15"
        )

    def test_models_str_methods_correct_values(self):
        self.assertEqual(str(self.group), self.group.title)
        self.assertEqual(str(self.post), self.post.text[:settings.FIFTEEN])

    def test_post_verbose_names(self):
        verbose_names_dict = {
            "author": "Автор",
            "group": "Группа",
            "pub_date": "Дата публикации",
            "text": "Текст",
        }
        for field, expected_value in verbose_names_dict.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )
