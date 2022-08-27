from django.core.paginator import Paginator
from django.conf import settings


def get_page_obj(request, posts_list, per_page=settings.POSTS_PER_PAGE):
    paginator = Paginator(posts_list, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
