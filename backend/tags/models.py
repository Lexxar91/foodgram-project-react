from django.db import models


class Tag(models.Model):
    """
    Модель для хранения информации о тегах.

    Атрибуты:
        name (str): Название тега (уникальное поле).
        color (str): Цвет тега (уникальное поле).
        slug (str): Уникальный идентификатор тега в формате слага.

    Мета:
        verbose_name (str): Название модели в единственном числе.
        verbose_name_plural (str): Название модели во множественном числе.

    Методы:
        __str__(): Возвращает строковое представление объекта тега.

    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название',
        help_text='Введите название тега'
    )
    color = models.CharField(
        max_length=8,
        unique=True,
        verbose_name='Цвет',
        help_text='Выберите цвет тега'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Cлаг',
        help_text='Введите слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
       return self.name
