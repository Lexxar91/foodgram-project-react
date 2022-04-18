from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='Почта'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Юзернейм'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя')
    
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия')
    
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150
    )
    def __str__(self):
        return f'{(self.username)}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор постов',
    )

    class Meta:
        models.UniqueConstraint(
            fields=('user', 'author',),
            name='unique_follow',
        )

    def __str__(self):
        return (f'{self.user.username} подписывается на автора '
                f'{self.author.username}')

