from http import HTTPStatus

from django import utils
from django.contrib.auth.tokens import default_token_generator
from django.test import Client, TestCase
from django.urls import reverse
from .test_views import User


class UsersTestUrls(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username="testuser")

        cls.url_templates_not_auth = {
            reverse(
                "users:login"
            ): "users/login.html",
            reverse(
                "users:password_reset"
            ): "users/password_reset_form.html",
            reverse(
                "users:password_reset_done"
            ): "users/password_reset_done.html",
            reverse(
                "users:password_reset_complete"
            ): "users/password_reset_complete.html",
            reverse(
                "users:signup"
            ): "users/signup.html",
        }
        cls.url_templates_auth = {
            reverse(
                "users:password_change"
            ): "users/password_change_form.html",
            reverse(
                "users:password_change_done"
            ): "users/password_change_done.html",
            reverse(
                "users:logout"
            ): "users/logged_out.html",
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_correct_templates_used_authorized(self):
        for url, template in self.url_templates_auth.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertTemplateUsed(response, template)

    def test_correct_templates_user_unauthorized(self):
        for url, template in self.url_templates_not_auth.items():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertTemplateUsed(response, template)

    def test_password_reset_codes_templates(self):
        uidb64 = utils.http.urlsafe_base64_encode(
            utils.encoding.force_bytes(self.user.id)
        )
        token = default_token_generator.make_token(self.user)
        url = f"/auth/reset/{uidb64}/{token}/"
        response = self.client.get(url, follow=True)

        self.assertTemplateUsed(response, "users/password_reset_confirm.html")

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_unathorized_to_login(self):
        urls = (
            reverse("users:password_change"),
            reverse("users:password_change_done"),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)

                self.assertRedirects(response, f"/auth/login/?next={url}")

    def test_url_codes_authorized(self):
        for url in self.url_templates_auth.keys():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_codes_unauthorized(self):
        for url in self.url_templates_not_auth.keys():
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)
