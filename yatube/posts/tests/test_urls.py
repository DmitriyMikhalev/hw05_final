from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


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
            group=cls.group,
            text="Some text"
        )

        cls.urls_templates = {
            reverse(
                "posts:group_list",
                kwargs={"slug": cls.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:index"
            ): "posts/index.html",
            reverse(
                "posts:post_create"
            ): "posts/create_post.html",
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

    def test_correct_template_404(self):
        response = self.client.get("something/does/not/exsist/")

        self.assertTemplateUsed(response, "core/404.html")

    def test_correct_templates_used(self):
        for url, template in self.urls_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertTemplateUsed(response, template)

    def test_redirect_not_author_edit_to_post_info(self):
        response = self.random_authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
            follow=True
        )

        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )

    def test_redirect_unathorized_to_login(self):
        urls = (
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
            reverse("posts:post_create"),
            reverse("posts:post_edit", kwargs={"post_id": self.post.id}),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)

                self.assertRedirects(response, f"/auth/login/?next={url}")

    def test_unexpected_url_code(self):
        response = self.authorized_client.get("/something/does/not/exists/")

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
