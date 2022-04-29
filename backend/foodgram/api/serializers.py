from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Exists
from rest_framework import serializers
from django.contrib.auth.password_validation import password_changed
from django.db.models import F
import webcolors
from drf_extra_fields.fields import Base64ImageField

from .validators import check_pass
from .variables import ALREADY_SIGNED, CANT_SUBSCRIBE_TO_YOURSELF, ERROR_CURRENT_PASSWORD, MAX_LEN_FOR_USERNAME, MIN_LEN_FOR_USERNAME, NOT_TRUE_PASSWORD, NOT_EMAIl_IN_DB
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from users.models import Follow, User


class ErrorResponse:
    
    FORBIDDEN_NAME = 'Это имя не может быть использовано!'
    MISSING_EMAIL = 'Для авторизации требуется ввести электронную почту'
    MISSING_USERNAME = 'Для аутентификации требуется ввести имя пользователя'
    MISSING_CODE = 'Для аутентификации требуется ввести код подтверждения'
    USERNAME_EXISTS = 'Пользователь с таким именем уже существует'
    EMAIL_EXISTS = 'Этот адрес электронной почты уже зарегестрирован'




class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
    extra_kwargs = {
        'password': {'write_only': True}
        }

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return Follow.objects.filter(
            user=user,
            author=obj.id
        )
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user
    
    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(ErrorResponse.FORBIDDEN_NAME)
        elif value is None or value == '':
            raise serializers.ValidationError(ErrorResponse.MISSING_USERNAME)
        return value

    def validate_username_len(self, value):
        if len(value) < MIN_LEN_FOR_USERNAME:
            raise serializers.ValidationError(f'Минимальная длина {MIN_LEN_FOR_USERNAME} символов')
        elif len(value) > MAX_LEN_FOR_USERNAME:
            raise serializers.ValidationError(f'Максимальное количество символов {MAX_LEN_FOR_USERNAME}')

    def validate_email(self, email):
        if email is None or email == "":
            raise serializers.ValidationError(ErrorResponse.MISSING_EMAIL)
        return email
        

class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_interval_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data

class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug',)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            AmountIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient.get('amount')
            )
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')

        recipe.image = validated_data.get(
            'image', recipe.image)
        recipe.name = validated_data.get(
            'name', recipe.name)
        recipe.text = validated_data.get(
            'text', recipe.text)
        recipe.cooking_time = validated_data.get(
            'cooking_time', recipe.cooking_time)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
             recipe.ingredients.clear()
             for ingredient in ingredients:
                 AmountIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient.get('amount')
            )
        recipe.save()
        return recipe
        

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        elif user.is_authenticated:
            return obj.is_favorited

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        elif user.is_authenticated:
            return obj.is_In_shopping_cart

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('ingredient_recipe__amount')
        )
        return ingredients

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['tags'] = TagSerializer(instance.tags.all(), many=True).data

        return result

class AmountRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(read_only=True)
    measurement_unit = serializers.CharField(read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )




class ListFollowSerializer(serializers.ModelSerializer):
    
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ( 
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
   
    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.only('id', 'name', 'image', 'cooking_time')

        if limit:
            recipes = recipes[limit]

        return RecipesForFavoriteSerializers(recipes, many=True).data
    
    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class FollowSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    author = serializers.PrimaryKeyRelatedField(queryset=queryset)
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    type_list = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'user',
            'author',
            'type_list'
        )

    def validate(self, data):
        user = data['user']
        author = data['author']

        if user == author:
            raise serializers.ValidationError(
                CANT_SUBSCRIBE_TO_YOURSELF
            )

        if Follow.objects.filter(user=user, author=author):
            raise serializers.ValidationError(
                f'{ALREADY_SIGNED} {author}.'
            )

        return data

    def create(self, validated_data):
        user = validated_data['user']
        author = validated_data['author']

        Follow.objects.create(
            user=user,
            author=author
        )

        return user

    def to_representation(self, instance):
       data = instance.subscribing.annotate(
            is_subscribed=Exists(User.objects.all())).last()

       return ListFollowSerializer(
            data,
            context={
                'request': self.context.get('request'),
            }
        ).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit',)


class ResetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=150)
    new_password = serializers.CharField(max_length=159)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        password_changed(validated_data['new_password'], user=instance)
        instance.save()

        return instance

    def validate_current_password(self, value):
        user = self.context.get('request').user 
        if user.check_password(value):
            return value
        raise ValidationError(ERROR_CURRENT_PASSWORD)

    def validate_new_password(self, value):
        return check_pass(value)


class RecipesForFavoriteSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class FavoriteAndShoppingSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    type_list = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'recipe',
            'user',
            'type_list',
        )

    def validate(self, data):
        recipe = get_object_or_404(Recipe, id=data['recipe'].id)

        if data['type_list'] == 'favorite':
            condition = User.objects.select_related('favorite_recipes').filter(
                username=data['user'].username,
                favorite_recipes=recipe
        )
        if data['type_list'] == 'shopping':
            condition = User.objects.select_related('shopping_recipes').filter(
                username=data['user'].username,
                shopping_recipes=recipe
        )
        if condition:
            raise serializers.ValidationError(
                    f"Рецепт {recipe} уже добавлен."
        )

        return data

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']

        if validated_data['type_list'] == 'favorite':
            user.favorite_recipes.add(recipe)
        if validated_data['type_list'] == 'shopping':
            user.shopping_recipes.add(recipe)

        return recipe

    def to_representation(self, instance):
       return RecipesForFavoriteSerializers(instance).data



class GetTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(max_length=128)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError(
                NOT_EMAIl_IN_DB
            )

        if user.check_password(data['password']):
            return data
        raise serializers.ValidationError(
            NOT_TRUE_PASSWORD
        )