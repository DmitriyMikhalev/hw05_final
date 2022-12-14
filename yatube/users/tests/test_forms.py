from django.test import TestCase
from django.urls import reverse
from .test_views import User


class UsersFormsTest(TestCase):
    def test_new_user_database(self):
        old_count_users = User.objects.count()

        form_data = {
            "username": "Har",
            "password1": "sZkl?ad315",
            "password2": "sZkl?ad315",
        }

        response = self.client.post(
            reverse("users:signup"),
            data=form_data,
            follow=True
        )

        self.assertEqual(User.objects.count(), old_count_users + 1)
        self.assertEqual(User.objects.filter(username="Har").exists(), True)

        self.assertRedirects(response, reverse("posts:index"))
