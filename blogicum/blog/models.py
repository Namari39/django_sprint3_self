from django.utils.timezone import now
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model


class BaseBlogMeta (models.Model):
    """
    Базовый мета-класс для моделей блога,
    определяющий общие атрибуты и настройки.

    Этот класс является абстрактным и не предназначен
    для создания объектов в базе данных.
    Он используется как основа для других моделей,
    предоставляя общие поля и параметры.

    Attributes:
        is_published (models.BooleanField): Флаг, указывающий,
            опубликован ли объект. По умолчанию установлен в True,
            объект считается опубликованным.
        created_at (models.DateTimeField): Дата и время создания объекта,
            устанавливаются автоматически при создании.

    Meta class:
        abstract: Указывает, что класс является абстрактным и не должен
            использоваться для создания таблицы в базе данных.
        ordering: Порядок сортировки объектов по умолчанию,
            в данном случае по полю 'created_at'.

    Примечание: Все модели, наследующиеся от этого класса,
    должны определить свои собственные поля и мета-параметры.
    """

    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True
        ordering = ('created_at', )


class PublishedPostsManager(models.Manager):
    def get_queryset(self):
        """
        Возвращает QuerySet с опубликованными публикациями,
        у которых дата публикации меньше текущего времени,
        и категория также опубликована. Результаты ограничены количеством,
        указанным в настройках для отображения на странице.
        """
        return super().get_queryset().select_related(
            'author', 'category', 'location'
        ).filter(
            is_published=True,
            pub_date__lt=now(),
            category__is_published=True,
        )


class Category(BaseBlogMeta):
    """
    Категория блога, представляющая собой набор связанных статей.

    Attributes:
        title (models.CharField): Заголовок категории.
            Используется в качестве основного имени.
        description (models.TextField): Описание категории,
            может содержать расширенную информацию.
        slug (models.SlugField): Уникальный идентификатор для использования
            в URL категории.

    Meta class:
        verbose_name: Название для одного объекта категории.
        verbose_name_plural: Название для множества объектов категорий.

    Methods:
        __str__: Возвращает строковое представление объекта,
            ограниченное длиной, определенной в настройках.
    """

    title = models.CharField(
        verbose_name='Заголовок',
        max_length=settings.MAX_FIELD_LENGTH
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=64, unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'''
        )
    )

    class Meta(BaseBlogMeta.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:settings.REPRESENTATION_LENGTH]


class Location(BaseBlogMeta):
    """
    Местоположение в контексте блога,
    используемое для группировки статей по географическому признаку.

    Attributes:
        name (models.CharField): Название местоположения.
            Используется для идентификации географического объекта.

    Meta class:
        verbose_name: Название для одного объекта местоположения.
        verbose_name_plural: Название для множества объектов местоположений.

    Methods:
        __str__: Возвращает строковое представление объекта местоположения,
            ограниченное длиной, определенной в настройках.
    """

    name = models.CharField(
        verbose_name='Название места',
        max_length=settings.MAX_FIELD_LENGTH
    )

    class Meta(BaseBlogMeta.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:settings.REPRESENTATION_LENGTH]


User = get_user_model()


class Post(BaseBlogMeta):
    """
    Представляет публикацию в блоге, содержащую заголовок, текст,
    информацию об авторе и прочее.

    Этот класс наследует от `BaseBlogMeta`, добавляя специфические поля
    и параметры для публикации статей.

    Attributes:
        title (models.CharField): Заголовок публикации.
            Ограничен максимальной длиной, определенной в настройках.
        text (models.TextField): Основной текст публикации.
        pub_date (models.DateTimeField): Дата и время публикации.
            Может быть использовано для отложенных публикаций.
        author (models.ForeignKey): Ссылка на пользователя,
            являющегося автором публикации.
        location (models.ForeignKey): Ссылка на местоположение,
            связанное с публикацией.
        category (models.ForeignKey): Ссылка на категорию,
            к которой относится публикация.

    Meta class:
        default_related_name: Имя, используемое
            для обратной связи в отношениях.
        verbose_name: Название для одного объекта публикации.
        verbose_name_plural: Название для множества объектов публикаций.
        ordering: Порядок сортировки объектов по умолчанию,
            в данном случае по убыванию даты публикации.

    Methods:
        __str__: Возвращает строковое представление публикации,
            ограниченное длиной, определенной в настройках.
    """

    title = models.CharField(
        verbose_name='Заголовок',
        max_length=settings.MAX_FIELD_LENGTH
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем '
            '— можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    objects = models.Manager()
    published = PublishedPostsManager()

    class Meta(BaseBlogMeta.Meta):
        default_related_name = 'posts'
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    def __str__(self) -> str:
        return self.title[:settings.REPRESENTATION_LENGTH]
