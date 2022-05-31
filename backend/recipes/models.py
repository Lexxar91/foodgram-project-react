from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Имя тэга',
        help_text='Введите название тега',
        max_length=120,
        db_index=True
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=30,
        help_text='Выберите цвет тега'
    )
    slug = models.CharField(
        verbose_name='Слаг',
        max_length=30,
        help_text='Введите слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'slug',),
                name='unique_name_slug',
            ),
        )
    
    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Имя ингредиента',
        max_length=80,
        help_text='Введите название ингредиента'
    )

    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=30,
        help_text='Введите единицу измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_name_measurement_unit',
            ),
        )


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        db_index=True,
        verbose_name='Автор рецепта',
        help_text='Введите автора'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Имя рецепта',
        help_text='Введите название рецепта',
        db_index=True,
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления(в минутах)',
        null=False,
        validators=(
            MinValueValidator(1, settings.MIN_COOKING_TIME),
        ),
    )
    image = models.ImageField(
        verbose_name='картинка',
        upload_to='recipes/',
        blank=True)
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата',
        help_text='Дата публикации'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='tag_recipe',
        help_text='Выберите теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        help_text='Выберите ингредиенты',
        related_name='recipe',
        through='IngredientsInRecipe',
        through_fields=('recipe', 'ingredient'),

    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text[:15]


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        help_text='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='Ингредиенты',
        help_text='Ингредиенты для рецепта')
    amount = models.PositiveIntegerField(
        'Количество', validators=(
            MinValueValidator(
                1, 'Мы же не воздух собираемся готовить?'), MaxValueValidator(
                1000, 'Где же взять столько денег на такое блюдо?')))

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingred_recipe'
            ),
        )
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return f'{self.ingredient} и {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранные рецепты',
        help_text='Избранные рецепты пользователя'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='users_favorites',
        verbose_name='Избранные у пользователей',
        help_text='Избранные рецепты у пользователей'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            ),
        )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

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
        verbose_name='В списке у пользователей',
        help_text='Рецепт в корзине пользователя'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe'
            ),
        )
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'
