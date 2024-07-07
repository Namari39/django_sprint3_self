from django.conf import settings
from django.shortcuts import render, get_object_or_404
from blog.models import Category, Post


def index(request):
    """
    Отображает главную страницу блога с перечнем опубликованных постов.
    Args:
        request: HttpRequest объект, содержащий метаданные о запросе.
    Returns:
        HttpResponse объект, рендерит 'blog/index.html'
        с контекстом, содержащим список постов.
    """
    post = Post.published.all()[:settings.POSTS_BY_PAGE]
    context = {
        'post_list': post
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id: int):
    """
    Отображает страницу с деталями конкретного поста блога.
    Использует кастомный менеджер `published` модели `Post`
    для получения объекта поста по его ID.
    Если пост с таким ID не найден или не опубликован, возвращает 404 ошибку.
    Args:
        request: HttpRequest объект, содержащий метаданные о запросе.
        post_id (int): Уникальный идентификатор поста для отображения.
    Returns:
        HttpResponse объект, рендерит 'blog/detail.html' с контекстом,
        содержащим детали поста.
    """
    post = get_object_or_404(
        Post.published.all(), id=post_id
    )
    context = {'post': post}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug: str):
    """
    Отображает страницу с постами блога, отфильтрованными по категории.
    Использует функцию `get_object_or_404` для получения объекта
    категории по её слагу,
    при этом проверяется, что категория опубликована (`is_published=True`).
    Далее, используя кастомный менеджер `published`,
    фильтрует посты по данной категории.
    Args:
        request: HttpRequest объект, содержащий метаданные о запросе.
        category_slug (str): Слаг категории,
            по которой необходимо отфильтровать посты.
    Returns:
        HttpResponse объект, рендерит 'blog/category.html' с контекстом,
        содержащим категорию и список постов.
    """
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True,
    )
    post = Post.published.filter(
        category__slug=category_slug
    )
    context = {
        'category': category,
        'post_list': post
    }
    return render(request, 'blog/category.html', context)
