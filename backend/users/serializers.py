import recipes
from django.conf import settings
from djoser.serializers import UserSerializer
from recipes.models import Recipe
from rest_framework import serializers

from users.models import Follow, User


class CurrentUserSerializer(UserSerializer):
    """
    Сериализатор для текущего пользователя.

    Атрибуты:
        is_subscribed (SerializerMethodField): Поле для определения, подписан ли текущий пользователь на данного пользователя.

    """
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        """
        Получает информацию о том, подписан ли текущий пользователь на данного пользователя.

        Args:
            obj (User): Объект пользователя, на которого проверяется подписка.

        Returns:
            bool: True, если текущий пользователь подписан, False в противном случае.

        """
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user, author=obj
        ).exists()

    def create(self, validated_data):
        """
        Создает нового пользователя.

        Args:
            validated_data (dict): Валидированные данные пользователя.

        Returns:
            User: Созданный пользователь.

        """
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user

    def validate_username(self, value):
        """
        Валидация имени пользователя.

        Args:
            value (str): Имя пользователя.

        Raises:
            serializers.ValidationError: Если имя пользователя запрещено (например, "me") или отсутствует.

        Returns:
            str: Проверенное имя пользователя.

        """
        if value == 'me':
            raise serializers.ValidationError(settings.FORBIDDEN_NAME)
        elif not value:
            raise serializers.ValidationError(settings.MISSING_USERNAME)
        return value

    def validate_username_len(self, value):
        """
        Валидация длины имени пользователя.

        Args:
            value (str): Имя пользователя.

        Raises:
            serializers.ValidationError: Если длина имени пользователя недостаточно короткая или слишком длинная.

        """
        if len(value) < settings.MIN_LEN_FOR_USERNAME:
            raise serializers.ValidationError(
                f'Минимальная длина {settings.MIN_LEN_FOR_USERNAME} символов')
        elif len(value) > settings.MAX_LEN_FOR_USERNAME:
            raise serializers.ValidationError(
                f'(Максимальное количество символов {settings.MAX_LEN_FOR_USERNAME}')

    def validate_email(self, email):
        """
        Валидация адреса электронной почты.

        Args:
            email (str): Адрес электронной почты.

        Raises:
            serializers.ValidationError: Если адрес электронной почты отсутствует.

        Returns:
            str: Проверенный адрес электронной почты.

        """
        if email is None or email == "":
            raise serializers.ValidationError(settings.MISSING_EMAIL)
        return email


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписки пользователя на другого пользователя.

    Мета:
        model (Follow): Модель подписки.
        fields (tuple): Поля, которые сериализуются.

    """

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def to_representation(self, instance):
        """
        Преобразует объект подписки в сериализованный формат.

        Args:
            instance (Follow): Объект подписки.

        Returns:
            dict: Сериализованный объект подписки.

        """
        request = self.context.get('request')
        context = {'request': request}
        serializer = SubscriptionSerializer(
            instance,
            context=context
        )
        return serializer.data

    def validate(self, data):
        """
        Валидация данных перед созданием подписки.

        Args:
            data (dict): Данные для создания подписки.

        Raises:
            serializers.ValidationError: Если пользователь пытается подписаться на самого себя или уже подписан на другого пользователя.

        Returns:
            dict: Валидированные данные для создания подписки.

        """
        user = data.get('user')
        author = data.get('author')
        if user == author:
            raise serializers.ValidationError(
                settings.CANT_SUBSCRIBE_TO_YOURSELF
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                settings.ALREADY_SIGNED
            )
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для подписки пользователя на другого пользователя.

    Атрибуты:
        email (ReadOnlyField): Адрес электронной почты пользователя.
        id (ReadOnlyField): Идентификатор пользователя.
        username (ReadOnlyField): Имя пользователя.
        first_name (ReadOnlyField): Имя пользователя.
        last_name (ReadOnlyField): Фамилия пользователя.
        is_subscribed (SerializerMethodField): Поле для определения, подписан ли текущий пользователь на данного пользователя.
        recipes (SerializerMethodField): Поле с информацией о рецептах пользователя.
        recipes_count (SerializerMethodField): Поле с количеством рецептов пользователя.

    Мета:
        model (Follow): Модель подписки.
        fields (tuple): Поля, которые сериализуются.

    """
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        """
        Получает информацию о том, подписан ли текущий пользователь на данного пользователя.

        Args:
            obj (Follow): Объект подписки.

        Returns:
            bool: True, если текущий пользователь подписан, False в противном случае.

        """
        request = self.context.get('request')
        return Follow.objects.filter(
            author=obj.author, user=request.user
        ).exists()

    def get_recipes(self, obj):
        """
        Получает информацию о рецептах пользователя, на которого подписан текущий пользователь.

        Args:
            obj (Follow): Объект подписки.

        Returns:
            list: Список сериализованных рецептов пользователя.

        """
        request = self.context.get('request')
        if request.GET.get('recipe_limit'):
            recipe_limit = int(request.GET.get('recipe_limit'))
            queryset = Recipe.objects.filter(
                author=obj.author)[:recipe_limit]
        else:
            queryset = Recipe.objects.filter(
                author=obj.author)
        serializer = recipes.serializers.ShortRecipeSerializer(
            queryset, read_only=True, many=True
        )
        return serializer.data

    def get_recipes_count(self, obj):
        """
        Получает количество рецептов пользователя, на которого подписан текущий пользователь.

        Args:
            obj (Follow): Объект подписки.

        Returns:
            int: Количество рецептов пользователя.

        """
        return obj.author.recipes.count()
