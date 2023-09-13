from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from recipes.filters import IngredientFilter, TagFilter
from recipes.mixins import RetrieveListMixins
from recipes.models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingCart)
from recipes.pagination import CustomPagination
from recipes.permissions import IsOwnerOrReadOnly
from recipes.serializers import (AddRecipeSerializer, IngredientSerializer,
                                 RecipeSerializer, ShortRecipeSerializer)
from recipes.utils import convert_txt


class IngredientViewSet(RetrieveListMixins):
    """
    ViewSet для ингредиентов.

    Атрибуты:
        queryset (QuerySet): Запрос для выборки ингредиентов из базы данных.
        serializer_class (Serializer): Сериализатор для ингредиентов.
        permission_classes (tuple): Кортеж с классами разрешений доступа.
        filterset_class (FilterSet): Фильтр для ингредиентов.

    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для рецептов.

    Атрибуты:
        queryset (QuerySet): Запрос для выборки рецептов из базы данных.
        permission_classes (tuple): Кортеж с классами разрешений доступа.
        pagination_class (Pagination): Класс пагинации для результатов запросов.
        filter_backends (tuple): Кортеж с бэкендами фильтрации.
        filterset_class (FilterSet): Фильтр для рецептов.

    """
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return AddRecipeSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """
        Добавление или удаление рецепта из избранного пользователя.

        Args:
            request (Request): Запрос.
            pk (int): Идентификатор рецепта.

        Returns:
            Response: Ответ с результатом операции.

        """
        if request.method == 'POST':
            return self.add_recipe(Favorite, request, pk)
        else:
            return self.delete_recipe(Favorite, request, pk)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Загрузка списка покупок в виде текстового файла.

        Args:
            request (Request): Запрос.

        Returns:
            Response: Текстовый файл с списком покупок.

        """
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))
        return convert_txt(ingredients)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """
        Добавление или удаление рецепта из списка покупок пользователя.

        Args:
            request (Request): Запрос.
            pk (int): Идентификатор рецепта.

        Returns:
            Response: Ответ с результатом операции.

        """
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, pk)
        else:
            return self.delete_recipe(ShoppingCart, request, pk)

    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if model.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError('Рецепт уже добавлен')
        model.objects.create(recipe=recipe, user=user)
        serializer = ShortRecipeSerializer(recipe)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        obj = get_object_or_404(model, recipe=recipe, user=user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)