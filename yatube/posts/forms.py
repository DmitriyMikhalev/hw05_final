from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        fields = ("group", "image", "text",)

        help_texts = {
            "group": "Группа, к которой должен относиться пост",
            "image": "Загрузите картинку",
            "text": "Введите текст",
        }

        model = Post


class CommentForm(forms.ModelForm):
    class Meta:
        fields = ("text",)

        help_texts = {
            "text": "Введите текст комментария",
        }

        model = Comment
