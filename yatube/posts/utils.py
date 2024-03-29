from django.core.paginator import Paginator

from .contstants import VARIABLE_POSTS


def imitation_of_page(request, post):
    """Оптимизированный метод пагинации для views-функции."""
    paginator = Paginator(post, VARIABLE_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return (page_obj)
