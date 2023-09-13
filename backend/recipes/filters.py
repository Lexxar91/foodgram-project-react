from django_filters.rest_framework import FilterSet, filters
from tags.models import Tag
from users.models import User

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """
    Фильтр для модели Ingredient.

    Атрибуты:
        name (CharFilter): Фильтр для поиска ингредиентов по началу имени.
    """
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)

class TagFilter(FilterSet):
    """
    Фильтр для модели Recipe с использованием тегов.

    Атрибуты:
        author (ModelChoiceFilter): Фильтр по автору рецепта.
        tags (ModelMultipleChoiceFilter): Фильтр по тегам рецепта.
        is_favorited (BooleanFilter): Фильтр по избранным рецептам.
        is_in_shopping_cart (BooleanFilter): Фильтр по рецептам в корзине.

    Методы:
        get_is_favorited(self, queryset, name, value):
            Получает рецепты, которые пользователь добавил в избранное.

        get_is_in_shopping_cart(self, queryset, name, value):
            Получает рецепты, которые пользователь добавил в корзину.
    """
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """
        Фильтр по избранным рецептам.

        Args:
            queryset (QuerySet): Начальный набор запросов.
            name (str): Имя поля фильтра.
            value (bool): Значение фильтра.

        Returns:
            QuerySet: Отфильтрованный набор запросов.
        """
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(users_favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтр по рецептам в корзине.

        Args:
            queryset (QuerySet): Начальный набор запросов.
            name (str): Имя поля фильтра.
            value (bool): Значение фильтра.

        Returns:
            QuerySet: Отфильтрованный набор запросов.
        """
        if self.request.user.is_authenticated and value is True:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
