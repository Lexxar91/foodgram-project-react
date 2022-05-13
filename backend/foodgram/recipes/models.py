from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from api.variables import MIN_COOKING_TIME
from users.models import User


class Tag(models.Model):
    name = models.CharField(verbose_name='Имя тэга',
                            max_length=120,
                            db_index=True
                            )
    color = models.CharField(verbose_name='color', max_length=30)
    slug = models.CharField(verbose_name='slug', max_length=30)

    class Meta:
        verbose_name = 'Тег'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'slug',),
                name='unique_name_slug',
            ),
        )

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(verbose_name='name', max_length=80)

    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=30
    )

    class Meta:
        verbose_name = 'Ингредиент'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_name_measurement_unit',
            ),
        )

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        db_index=True
    )
    name = models.CharField(max_length=200, verbose_name='name', db_index=True)
    text = models.TextField(verbose_name='text')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления(в минутах)',
        null=False,
        validators=(
            MinValueValidator(1, MIN_COOKING_TIME),
        ),
    )
    image = models.ImageField(
        verbose_name='картинка',
        upload_to='recipes/',
        blank=True)
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='pub_date')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тэг',
        related_name='tag_recipe',

    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ингредиенты',
        related_name='recipe',
        through='IngredientsInRecipe',
        through_fields=('recipe', 'ingredient'),

    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='ингредиенты',)
    amount = models.PositiveIntegerField(
        'Количество', validators=(
            MinValueValidator(
                1, 'Мы же не воздух собираемся готовить?'), MaxValueValidator(
                1000, 'Где же взять столько денег на такое блюдо?')))

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingred_recipe'
            ),
        )

    def __str__(self):
        return f'{self.ingredient} и {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранные рецепты'

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='users_favorites',
        verbose_name='Избранные у пользователей'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Список покупок',
        help_text='Список покупок пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='В списке у пользователей'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'
