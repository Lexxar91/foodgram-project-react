import users.serializers as users
from django.conf import settings
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, validators
from tags.models import Tag
from tags.serializers import TagField

from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingCart)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.

    Атрибуты:
        Meta (class): Класс Meta с информацией о модели и полях, которые следует сериализовать.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'

class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели IngredientsInRecipe.

    Атрибуты:
        Meta (class): Класс Meta с информацией о модели и полях, которые следует сериализовать.
        validators (tuple): Валидаторы, включая уникальность.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    validators = (
        validators.UniqueTogetherValidator(
            queryset=IngredientsInRecipe.objects.all(),
            fields=('ingredient', 'recipe')
        ),
    )

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'

class AddIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления ингредиентов в рецепт.

    Атрибуты:
        Meta (class): Класс Meta с информацией о модели и полях, которые следует сериализовать.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount')

class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe.

    Атрибуты:
        author (CurrentUserSerializer): Сериализатор для текущего автора рецепта.
        tags (TagField): Поле для сериализации тегов.
        ingredients (IngredientInRecipeSerializer): Сериализатор для ингредиентов в рецепте.
        is_favorited (SerializerMethodField): Поле для определения, добавлен ли рецепт в избранное.
        is_in_shopping_cart (SerializerMethodField): Поле для определения, добавлен ли рецепт в корзину.

    Атрибуты Meta:
        model (class): Модель, которую сериализуем.
        fields (tuple): Поля модели, которые следует сериализовать.
    """
    author = users.CurrentUserSerializer()
    tags = TagField(
        slug_field='id', queryset=Tag.objects.all(), many=True
    )
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_in_recipe',
        read_only=True, many=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'name',
            'author',
            'ingredients',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def in_list(self, obj, model):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self.in_list(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.in_list(obj, ShoppingCart)

class AddRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецепта.

    Атрибуты:
        tags (PrimaryKeyRelatedField): Поле для сериализации тегов.
        ingredients (AddIngredientSerializer): Сериализатор для ингредиентов.
        image (Base64ImageField): Поле для загрузки изображения блюда.

    Методы:
        to_representation(self, instance): Преобразует объект рецепта в представление.
        create_ingredients(self, ingredients, recipe): Создает связи между рецептом и ингредиентами.
        create(self, validated_data): Создает новый рецепт и связи с ингредиентами и тегами.
        update(self, instance, validated_data): Обновляет существующий рецепт и связи с ингредиентами и тегами.
        validate(self, data): Проверяет корректность данных перед созданием рецепта.
        validate_cooking_time(self, data): Проверяет корректность времени приготовления.

    Метаданные:
        model (class): Модель, которую сериализуем.
        fields (tuple): Поля модели, которые следует сериализовать.
    """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField(max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'name',
            'ingredients',
            'image',
            'text',
            'cooking_time'
        )

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance)
        return serializer.data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = ingredient['id']
            IngredientsInRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.save()
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.create_ingredients(ingredients, instance)
        instance.tags.clear()
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def validate(self, data):
        ings = data['ingredients']
        if not ings:
            raise serializers.ValidationError(
                settings.THE_FIELD_WITH_INGREDIENTS_CANNOT_BE_EMPTY
            )
        unique_ings = []
        for ingredient in ings:
            name = ingredient['id']
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    f'Не корректное количество для {name}'
                )
            if not isinstance(ingredient['amount'], int):
                raise serializers.ValidationError(
                    settings.MUST_BE_INTEGER
                )
            if name not in unique_ings:
                unique_ings.append(name)
            else:
                raise serializers.ValidationError(
                    settings.NOT_REPEATS_INGREDIENTS
                )
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше 1 минуты'
            )
        return data

class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для представления краткой информации о рецепте.

    Метаданные:
        model (class): Модель, которую сериализуем.
        fields (tuple): Поля модели, которые следует сериализовать.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')