from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Почта',
        help_text='Введите адрес электронной почты'
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=30,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
    )

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
        return f'{self.username}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        help_text='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор постов',
        help_text='Автор постов'
    )

    class Meta:
        models.UniqueConstraint(
            fields=('user', 'author',),
            name='unique_follow',
        )
        models.CheckConstraint(
            check=models.Q(user=models.F('user_author')),
            name='check_user',
        ),
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
    
    def __str__(self):
        return (f'{self.user.username} подписывается на автора '
                f'{self.author.username}')
