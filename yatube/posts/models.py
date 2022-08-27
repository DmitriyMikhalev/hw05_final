from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from core.models import AbstractModel
from django.db.models import F

User = get_user_model()


class Post(AbstractModel):
    author = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="posts",
        to=User,
        verbose_name="Автор"
    )
    group = models.ForeignKey(
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        to="Group",
        verbose_name="Группа"
    )
    text = models.TextField(
        verbose_name="Текст"
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="posts/",
        blank=True
    )

    class Meta:
        ordering = [F("pub_date").desc(nulls_last=True)]
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"

    def __str__(self):
        return self.text[:settings.FIFTEEN]


class Group(models.Model):
    description = models.TextField(
        verbose_name="Описание"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Адрес"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Название"
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Comment(AbstractModel):
    author = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="comments",
        to=User,
        verbose_name="Автор комментария"
    )
    post = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="comments",
        to=Post,
        verbose_name="Комментарий"
    )
    text = models.TextField(
        verbose_name="Содержание комментария"
    )

    class Meta:
        ordering = [F("pub_date").desc(nulls_last=True)]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:settings.FIFTEEN]


class Follow(models.Model):
    author = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="following",
        to=User,
        verbose_name="Автор"
    )
    user = models.ForeignKey(
        on_delete=models.CASCADE,
        related_name="follower",
        to=User,
        verbose_name="Подписчик"
    )

    class Meta:
        ordering = [F("author").desc(nulls_last=True)]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
