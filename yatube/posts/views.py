from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import get_page_obj


@cache_page(timeout=settings.CACHE_TIME, key_prefix="index_page")
@vary_on_cookie
def index(request):
    template = "posts/index.html"

    posts_list = Post.objects.all()
    page_obj = get_page_obj(request, posts_list)

    context = {
        "page_obj": page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = "posts/group_list.html"

    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = get_page_obj(request, posts_list)

    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = "posts/profile.html"

    user = get_object_or_404(
        User,
        username=username
    )
    page_obj = get_page_obj(request, user.posts.all())
    following = Follow.objects.filter(author=user, user=request.user).exists()

    context = {
        "page_obj": page_obj,
        "user_obj": user,
        "following": following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"

    form = CommentForm()

    post = get_object_or_404(Post, pk=post_id)
    post_comments = Comment.objects.filter(post__id=post_id)
    posts_count = Post.objects.filter(author=post.author).count()

    context = {
        "form": form,
        "post": post,
        "post_comments": post_comments,
        "posts_count": posts_count,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if not form.is_valid():
        return render(request, "posts/create_post.html", {"form": form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("posts:profile", username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if not form.is_valid():
        context = {
            "form": form,
            "is_edit": True,
            "post": post
        }
        return render(request, "posts/create_post.html", context)

    form.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_obj(request, posts)

    return render(request, "posts/follow.html", {'page_obj': page_obj})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)

    if not (author == request.user or Follow.objects.filter(
        author=author,
        user=request.user).exists()
    ):
        Follow.objects.create(author=author, user=request.user)

    return redirect(reverse("posts:profile", kwargs={"username": username}))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)

    if not (author == request.user or not Follow.objects.filter(
        author=author,
        user=request.user).exists()
    ):
        Follow.objects.get(author=author, user=request.user).delete()

    return redirect(reverse("posts:profile", kwargs={"username": username}))
