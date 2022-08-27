from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    empty_value_display = "-пусто-"
    list_display = ("pk", "text", "pub_date", "author", "group")
    list_editable = ("group",)
    list_filter = ("author", "pub_date")
    search_fields = ("text",)


class CommentAdmin(admin.ModelAdmin):
    empty_value_display = "-пусто-"
    list_display = ("pk", "text", "pub_date", "author")
    list_editable = ("text",)
    list_filter = ("author", "pub_date", "text")
    search_fields = ("text",)


class FollowAdmin(admin.ModelAdmin):
    empty_value_display = "-пусто-"
    list_display = ("pk", "author", "user")
    list_filter = ("author", "user")


admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Group)
admin.site.register(Post, PostAdmin)
