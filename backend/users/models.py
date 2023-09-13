from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Расширенная модель пользователя.

    Атрибуты:
        email (str): Адрес электронной почты пользователя (уникальное поле).
        USERNAME_FIELD (str): Поле, используемое для аутентификации (в данном случае - email).
        REQUIRED_FIELDS (list): Список обязательных полей при создании пользователя.

    Мета:
        verbose_name (str): Название модели в единственном числе.
        verbose_name_plural (str): Название модели во множественном числе.
        ordering (tuple): Порядок сортировки объектов модели (по умолчанию - по username).
        constraints (tuple): Ограничения базы данных (уникальное сочетание username и email).

    Методы:
        __str__(): Возвращает строковое представление объекта пользователя.

    """
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='email',
        help_text='Введите адрес электронной почты'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email',),
                name='unique_username_email',
            ),
        )

    def __str__(self):
        return self.username


class Follow(models.Model):
    """
    Модель для хранения информации о подписках пользователей.

    Атрибуты:
        user (User): Подписчик.
        author (User): Отслеживаемый автор.

    Мета:
        constraints (tuple): Ограничения базы данных (уникальная подписка).
        verbose_name (str): Название модели в единственном числе.
        verbose_name_plural (str): Название модели во множественном числе.

    Методы:
        __str__(): Возвращает строковое представление объекта подписки.

    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Отслеживаемый автор'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписался {self.author}'