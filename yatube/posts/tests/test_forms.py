import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.form = PostForm()

        cls.group = Group.objects.create(
            description="This is a group.. I hope.",
            slug="slugy",
            title="Тестовое название"
        )

        cls.user = User.objects.create_user(
            username="Harold"
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text="!?....",
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_comment_database(self):
        old_count_comments = Comment.objects.count()

        form_data = {
            "author": self.user,
            "post": self.post,
            "text": "test"
        }

        self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.id}),
            data=form_data,
            follow=True
        )

        self.assertEqual(Comment.objects.count(), old_count_comments + 1)
        self.assertEqual(Comment.objects.filter(**form_data).exists(), True)

    def test_create_new_post_database(self):
        old_count_posts = Post.objects.count()

        form_data = {
            "author": self.user,
            "text": "Test text new post",
        }

        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )

        self.assertEqual(
            Post.objects.count(),
            old_count_posts + 1
        )
        self.assertEqual(
            Post.objects.filter(**form_data).exists(),
            True
        )
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            )
        )

    def test_create_new_post_database_image(self):
        old_count_posts = Post.objects.count()

        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )

        form_data = {
            "author": self.user,
            "text": "Test text new post",
            "image": uploaded
        }

        response = self.authorized_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True
        )

        self.assertEqual(
            Post.objects.count(),
            old_count_posts + 1
        )
        self.assertEqual(
            Post.objects.filter(
                author=self.user,
                text="Test text new post",
                image="posts/small.gif"
            ).exists(),
            True
        )

        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={"username": self.user.username}
            )
        )

    def test_edit_post_database(self):
        posts_count = Post.objects.count()

        form_data = {
            "author": self.user,
            "text": "Test edited",
        }

        response = self.authorized_client.post(
            reverse(
                "posts:post_edit",
                kwargs={"post_id": self.post.id}
            ),
            data=form_data,
            follow=True
        )

        self.assertEqual(
            posts_count,
            Post.objects.count()
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id),
            Post.objects.get(**form_data)
        )

        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={"post_id": self.post.id}
            )
        )

    def test_help_texts(self):
        expected_help_texts = {
            "group": "Группа, к которой должен относиться пост",
            "text": "Введите текст",
        }
        for field, expected_help_text in expected_help_texts.items():
            with self.subTest(field=field):
                help_text = self.form.fields[field].help_text

                self.assertEqual(help_text, expected_help_text)
