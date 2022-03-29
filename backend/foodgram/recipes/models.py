from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class Tag(models.Model):
    name = models.CharField(verbose_name='name',
     max_length=120,
     db_index=True
     )
    color = models.CharField(verbose_name='color', max_length=30)
    slug = models.CharField(verbose_name='slug', max_length=30)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    MEASUREMENT_UNIT = (
        ('кг', 'кг'),
        ('грамм', 'грамм'),
        ('литр', 'литр'),
        ('литров', 'литров'),
        ('мл', 'мл'),
    )
    name = models.CharField(verbose_name='name', max_length=80)
    measurement_unit = models.CharField(
        verbose_name='measurement_unit',
        choices=MEASUREMENT_UNIT,
        max_length=30
    )

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        db_index=True
    )
    name = models.CharField(max_length=200, verbose_name='name', db_index=True)
    text = models.TextField(verbose_name='text')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления(в минутах)',
        null=False,
        validators=(
            MinValueValidator(1, 'Время приготовления не может быть меньше 1 минуты!'),
        ),
    )
    image = models.ImageField(
        verbose_name='image',
         upload_to='recipes/',
         blank=True)
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='pub_date')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='tag',
        related_name='tag_recipe',
        blank=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='ingridient',
        related_name='recipe',
        blank=True
    )
    class Meta:
        ordering = ('-pub_date',)
    
    def __str__(self):
        return self.text[:6]


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='recipe',
        on_delete=models.CASCADE,
        related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name='ingredient',)
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(
            MinValueValidator(1, 'Мы же не воздух собираемся готовить?'),
            MaxValueValidator(1000, 'Где же взять столько денег на такое блюдо?')
        ))

    class Meta:
        constraints=(
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingred_recipe'
            ),
        )

    def __str__(self):
        return f'{self.ingredient}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='user',)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='recipe',)

    class Meta:
        constraints=(
        models.UniqueConstraint(
            fields=('user', 'recipe',),
            name='unique_favorite'
        ),
    )

    def __str__(self):
        return f'{self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='user',)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='recipe',)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shop'),)

    def __str__(self):
        return f'{self.recipe}'