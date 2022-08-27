from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post


User = get_user_model()


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.random_user = User.objects.create_user(
            username="randomguest"
        )
        cls.user = User.objects.create_user(
            username="testuser"
        )

        cls.group = Group.objects.create(
            description="Тестовое описание",
            slug="test-slug",
            title="Тестовое название"
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text="Test text post has group"
        )
        cls.post_has_group = Post.objects.create(
            author=cls.user,
            text="Some text",
            group=cls.group
        )

        cls.urls_templates = {
            reverse(
                "posts:index"
            ): "posts/index.html",
            reverse(
                "posts:post_create"
            ): "posts/create_post.html",
            reverse(
                "posts:group_list",
                kwargs={"slug": cls.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": cls.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": cls.post.id}
            ): "posts/create_post.html",
            reverse(
                "posts:profile", kwargs={"username": cls.user.username}
            ): "posts/profile.html",
        }

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.random_authorized_client = Client()
        cls.random_authorized_client.force_login(cls.random_user)

    def test_allowed_urls_codes(self):
        for url in self.urls_templates.keys():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_unathorized_login(self):
        urls = (
            reverse("posts:post_create"),
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)

                self.assertRedirects(response, f"/auth/login/?next={url}")

    def test_redirect_not_author_edit_to_post_info(self):
        response = self.random_authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )

        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )

    def test_unexpected_url_code(self):
        response = self.authorized_client.get("/something/does/not/exist/")

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_correct_templates_used(self):
        for url, template in self.urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertTemplateUsed(response, template)

    def test_correct_template_404(self):
        response = self.client.get("something/does/not/exsist/")

        self.assertTemplateUsed(response, "core/404.html")