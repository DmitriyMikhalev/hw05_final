from django import forms, utils
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.forms import models
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.url_templates_authorized = {
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
        self.authorized_user = User.objects.create_user(
            username="authorized"
        )
        self.authorized_client.force_login(self.authorized_user)

        self.unauthorized_user = User.objects.create_user(
            username="unauthorized"
        )

    def test_signup_use_correct_context(self):
        response = self.client.get(reverse("users:signup"))
        form_obj = response.context.get("form")

        form_field_types = {
            "email": forms.fields.EmailField,
            "first_name": forms.fields.CharField,
            "last_name": forms.fields.CharField,
            "username": forms.fields.CharField,
        }
        for field, expected_type in form_field_types.items():
            with self.subTest(field=field):

                self.assertIsInstance(
                    form_obj.fields.get(field),
                    expected_type
                )

        self.assertIsInstance(form_obj, models.ModelForm)

    def test_view_funcs_use_correct_template_authorized(self):
        for url, template in self.url_templates_authorized.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertTemplateUsed(response, template)

    def test_view_funcs_use_correct_template_unauthorized(self):
        uidb64 = utils.http.urlsafe_base64_encode(
            utils.encoding.force_bytes(self.unauthorized_user.id)
        )
        token = default_token_generator.make_token(self.unauthorized_user)

        url_templates_unauthorized = {
            reverse(
                "users:login"
            ): "users/login.html",
            reverse(
                "users:password_reset"
            ): "users/password_reset_form.html",
            reverse(
                "users:password_reset_complete"
            ): "users/password_reset_complete.html",
            reverse(
                "users:password_reset_confirm",
                kwargs={"uidb64": uidb64, "token": token}
            ): "users/password_reset_confirm.html",
            reverse(
                "users:password_reset_done"
            ): "users/password_reset_done.html",
            reverse(
                "users:signup"
            ): "users/signup.html",
        }
        for url, template in url_templates_unauthorized.items():
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)

                self.assertTemplateUsed(response, template)
