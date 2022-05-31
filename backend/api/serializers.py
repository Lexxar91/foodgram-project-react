from django.conf import settings
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Follow, User


class CurrentUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')

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
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj.id
        ).exists()

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(settings.FORBIDDEN_NAME)
        elif not value:
            raise serializers.ValidationError(settings.MISSING_USERNAME)
        return value

    def validate_username_len(self, value):
        if len(value) < settings.MIN_LEN_FOR_USERNAME:
            raise serializers.ValidationError(
                f'Минимальная длина {settings.MIN_LEN_FOR_USERNAME} символов')
        elif len(value) > settings.MAX_LEN_FOR_USERNAME:
            raise serializers.ValidationError(
                f'(Максимальное количество символов {settings.MAX_LEN_FOR_USERNAME}')

    def validate_email(self, email):
        if email is None or email == "":
            raise serializers.ValidationError(settings.MISSING_EMAIL)
        return email


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class TagField(serializers.SlugRelatedField):

    def to_representation(self, value):
        request = self.context.get('request')
        context = {'request': request}
        serializer = TagSerializer(value, context=context)
        return serializer.data


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()
    amount = serializers.ReadOnlyField()
    
    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    author = CurrentUserSerializer()
    tags = TagField(
        slug_field='id',
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientInRecipeSerializer(
        read_only=True, many=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

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

    def in_list(self, obj, model):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return model.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self.in_list(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.in_list(obj, ShoppingCart)


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = (
            'user',
            'author',
        )
    
    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        serializer = SubscriptionSerializer(
            instance,
            context=context
        )
        return serializer.data

    def validate(self, data):
        user = data['user']
        author = data['author']

        if user == author:
            raise serializers.ValidationError(
                settings.CANT_SUBSCRIBE_TO_YOURSELF
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
            'Вы уже подписаны на этого пользователя!'
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


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')
   
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

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return Follow.objects.filter(user=user).exists()
        
    def get_recipes(self, obj):
        request = self.context['request']
        limit = int(request.query_params.get('recipes_limit', 3))
        recipes = Recipe.objects.all()[:limit]
        serializer = RecipesForFavoriteSerializers(
            recipes,
            many=True,
            context={'request': request},
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.count()


class AddRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'tags',
            'name',
            'ingredients',
            'image',
            'text',
            'cooking_time',
        )

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

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
        return data


class RecipesForFavoriteSerializers(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )
