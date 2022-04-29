from django.db import models
from django.contrib.auth.models import AbstractUser

from recipes.models import Recipe


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
        verbose_name='Имя'
    )
    
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )
    
    password = models.CharField(
        verbose_name='Пароль',
        max_length=150
    )
    subscribing = models.ManyToManyField(
        to='self',
        through='Follow',
        verbose_name='Подписчики',
    )
    favorite_recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Избранные рецепты',
        related_name='favorites',
    )
    shopping_cart = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты в списке покупок',
        related_name='shoppings_cart',
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password',
    )

    class Meta:
        verbose_name = 'Пользователь'
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
        models.CheckConstraint(
            check= models.Q(user=models.F('user_author')),
            name='check_user',
        ),

    def __str__(self):
        return (f'{self.user.username} подписывается на автора '
                f'{self.author.username}')

