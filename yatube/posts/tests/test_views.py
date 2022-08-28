import shutil
import tempfile
from time import sleep

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

from ..forms import PostForm

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="qwerty"
        )

        cls.group = Group.objects.create(
            description="Тестовое описание",
            slug="test-slug",
            title="Тестовое название"
        )

        for i in range(15, 0, -1):
            Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f"{i} number of post"
            )
            sleep(1E-6)

    def test_paginator(self):
        urls = (
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            ),
            reverse(
                "posts:index"
            ),
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            ),
        )
        for url in urls:
            with self.subTest(url=url):
                for page in (1, 2):
                    response = self.client.get(f"{url}?page={page}")
                    page_obj = response.context.get("page_obj")

                    self.assertEqual(
                        len(page_obj),
                        settings.POSTS_PER_PAGE if page == 1 else
                        Post.objects.count() - settings.POSTS_PER_PAGE
                    )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    def check_page_obj_at_context(self, response):
        """This function is a part of simple context testing.
        It was created in order not to create duplicate constructs in each view
        function, since many of them pass the page_obj object to the context.
        Get 1 required argument response, type TemplateResponse."""
        first_object_post = response.context.get("page_obj")[0]

        self.assertEqual(first_object_post.author.username, "TestUser")
        self.assertEqual(first_object_post.text, "test test")
        self.assertEqual(first_object_post.group.title, "Тестовое название")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            content=cls.small_gif,
            content_type="image/gif",
            name="small.gif"
        )

        cls.user = User.objects.create_user(
            username="TestUser"
        )
        cls.random_user = User.objects.create_user(
            username="RandomUser"
        )

        cls.group = Group.objects.create(
            description="Тестовое описание",
            slug="Test-slug",
            title="Тестовое название"
        )
        cls.group_2 = Group.objects.create(
            description="Тестовое описание второй группы",
            slug="test-slug-group-2",
            title="Тестовое название второй группы"
        )

        cls.test_post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
            text="test test"
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.test_post,
            text="test"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_cache(self):
        response = self.authorized_client.get(reverse("posts:index"))
        posts = response.content

        self.post = Post.objects.create(
            author=self.user,
            text="doesnt matter"
        )

        new_response = self.authorized_client.get(reverse("posts:index"))
        new_posts = new_response.content

        self.assertEqual(posts, new_posts)

    def test_comment_at_post_detail(self):
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.test_post.id})
        )

        comment_obj = response.context.get("post_comments")[0]

        self.assertEqual(comment_obj, self.comment)

    def test_group_posts_use_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            )
        )

        self.assertEqual(
            response.context.get("group"),
            Group.objects.get(id=1)
        )
        self.assertEqual(
            response.context.get("page_obj")[0].image,
            "posts/small.gif"
        )

        self.check_page_obj_at_context(response)

    def test_index_use_correct_context(self):
        response = self.authorized_client.get(reverse("posts:index"))

        self.assertEqual(
            response.context.get("page_obj")[0].image,
            "posts/small.gif"
        )

        self.check_page_obj_at_context(response)

    def test_post_create_use_correct_context(self):
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_obj = response.context.get("form")

        form_field_types = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
        }

        for field, expected_type in form_field_types.items():
            with self.subTest(field=field):
                field_type = form_obj.fields.get(field)

                self.assertIsInstance(field_type, expected_type)

        self.assertIsInstance(form_obj, PostForm)

    def test_post_created_at_right_group_and_profile(self):
        """Testing post was not created in the wrong profile and group"""
        urls = (
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group_2.slug}
            ),
            reverse(
                "posts:profile",
                kwargs={"username": self.random_user.username}
            )
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                page_obj = response.context.get("page_obj")

                self.assertEqual(len(page_obj), 0)

    def test_post_detail_use_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.test_post.id}
            )
        )

        post_obj = response.context.get("post")
        posts_count = response.context.get("posts_count")
        expected_count = Post.objects.filter(author=post_obj.author).count()

        self.assertEqual(
            post_obj,
            self.test_post
        )
        self.assertEqual(
            response.context.get("post").image,
            "posts/small.gif"
        )
        self.assertEqual(
            posts_count,
            expected_count
        )

    def test_post_edit_use_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.test_post.id}
            )
        )

        form_obj = response.context.get("form")
        form_obj_group = form_obj["group"].__getitem__(1).choice_label
        form_obj_text = form_obj["text"].value()

        expected_fields = {
            "group": "Тестовое название",
            "text": "test test",
        }

        self.assertEqual(response.context.get("post"), self.test_post)
        self.assertEqual(response.context.get("is_edit"), True)

        self.assertEqual(form_obj_group, expected_fields.get("group"))
        self.assertEqual(form_obj_text, expected_fields.get("text"))

        self.assertIsInstance(form_obj, PostForm)

    def test_profile_use_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            )
        )

        self.assertEqual(
            response.context.get("user_obj"),
            self.user
        )
        self.assertEqual(
            response.context.get("page_obj")[0].image,
            "posts/small.gif"
        )

        self.check_page_obj_at_context(response)

    def test_view_funcs_use_correct_templates(self):
        cache.clear()

        names_templates = {
            reverse(
                "posts:group_list",
                kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:index"
            ): "posts/index.html",
            reverse(
                "posts:post_create"
            ): "posts/create_post.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.test_post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.test_post.id}
            ): "posts/create_post.html",
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            ): "posts/profile.html",
        }
        for url, template in names_templates.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertTemplateUsed(response, template)


class TestSubscriptions(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author_user = User.objects.create_user(
            username="username 1"
        )
        cls.follower_user = User.objects.create_user(
            username="username 3"
        )
        cls.random_user = User.objects.create_user(
            username="username 2"
        )

        cls.author_client = Client()
        cls.author_client.force_login(cls.author_user)

        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower_user)

        cls.random_client = Client()
        cls.random_client.force_login(cls.random_user)

        cls.post = Post.objects.create(
            author=cls.author_user,
            text="test"
        )

    def setUp(self):
        self.follower_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author_user.username}
            )
        )

    def test_follow_view(self):
        old_count_follows = Follow.objects.count()

        self.random_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.author_user.username}
            )
        )

        self.assertEqual(old_count_follows + 1, Follow.objects.count())

    def test_post_shows_only_for_followers(self):
        url = reverse("posts:follow_index")

        response_follower = self.follower_client.get(url)
        response_random_user = self.random_client.get(url)

        page_obj_follower = response_follower.context.get("page_obj")
        page_obj_random_user = response_random_user.context.get("page_obj")

        self.assertNotEqual(len(page_obj_follower), len(page_obj_random_user))

    def test_unfollow_view(self):
        old_count_follows = Follow.objects.count()

        self.follower_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.author_user.username}
            )
        )

        self.assertEqual(old_count_follows - 1, Follow.objects.count())
