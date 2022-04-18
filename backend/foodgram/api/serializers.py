from django.forms import ValidationError
from rest_framework import serializers
from django.contrib.auth.password_validation import password_changed
from djoser.serializers import UserCreateSerializer as DjoserCreateUser, UserSerializer
from django.db.models import F
import webcolors
from drf_extra_fields.fields import Base64ImageField

from .validators import check_pass
from .variables import ERROR_CURRENT_PASSWORD, MAX_LEN_FOR_USERNAME, MIN_LEN_FOR_USERNAME
from recipes.models import AmountIngredient, Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, User

## 13/04  переделать модель юзер

class ErrorResponse:
    
    FORBIDDEN_NAME = 'Это имя не может быть использовано!'
    MISSING_EMAIL = 'Для авторизации требуется ввести электронную почту'
    MISSING_USERNAME = 'Для аутентификации требуется ввести имя пользователя'
    MISSING_CODE = 'Для аутентификации требуется ввести код подтверждения'
    USERNAME_EXISTS = 'Пользователь с таким именем уже существует'
    EMAIL_EXISTS = 'Этот адрес электронной почты уже зарегестрирован'

class UserCreateSerializer(DjoserCreateUser):
    class Meta(DjoserCreateUser.Meta):
        fields = ('email','username','first_name','last_name','password')

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

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return Follow.objects.filter(
            user=user,
            author=obj.id
        )
    
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
    author = UserSerializer(read_only=True)
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
        return Favorite.objects.filter(user=user,recipe=obj.id)

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe_in_shop_cart=obj.id)

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('ingredient_recipe__amount')
        )
        return ingredients





class ForFollowFieldsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FollowSerializer(serializers.ModelSerializer):
    
    recipes = ForFollowFieldsSerializer(many=True, read_only=True)
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
   
    
    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


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



