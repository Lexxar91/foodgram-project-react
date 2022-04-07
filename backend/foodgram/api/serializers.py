from rest_framework import serializers
import webcolors
from drf_extra_fields.fields import Base64ImageField
from backend.foodgram.recipes.models import Favorite, Recipe, ShoppingCart, Tag
from backend.foodgram.users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return Follow.objects.filter(
            user=user,
            author=obj.id
        )
        

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
    color = Hex2NameColor

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug',)

class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=True)
    image = Base64ImageField()
    
    class Meta:
        model = Recipe
        fields = '__all__'

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


class FollowSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    class Meta:
        model = Follow
        fields = ()

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()