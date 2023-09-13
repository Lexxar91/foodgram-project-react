from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingCart)


class RecipeAdmin(admin.ModelAdmin):
    """
    Админка для модели Recipe.

    Атрибуты:
        list_display (tuple): Поля для отображения в списке записей.
        search_fields (tuple): Поля для поиска в панели администратора.
        readonly_fields (tuple): Поля, доступные только для чтения в панели администратора.
        list_filter (tuple): Поля для фильтрации списка записей.
    """

    list_display = (
        'name',
        'author',
    )
    search_fields = (
        'name',
        'author__username',
        'author__email',
    )
    readonly_fields = ('favorite_count',)
    list_filter = ('author', 'name', 'tags',)

    def favorite_count(self, obj):
        """
        Пользовательский метод для отображения количества избранных рецептов.

        Аргументы:
            obj (Recipe): Экземпляр модели Recipe.

        Возвращает:
            int: Количество избранных рецептов для данного рецепта.
        """
        return obj.favorite_recipe.count()

class IngredientAdmin(admin.ModelAdmin):
    """
    Админка для модели Ingredient.

    Атрибуты:
        list_display (tuple): Поля для отображения в списке записей.
        search_fields (tuple): Поля для поиска в панели администратора.
        list_filter (tuple): Поля для фильтрации списка записей.
    """

    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('measurement_unit',)
    list_filter = ('measurement_unit',)

class IngredientsInRecipeAdmin(admin.ModelAdmin):
    """
    Админка для модели IngredientsInRecipe.

    Атрибуты:
        list_display (tuple): Поля для отображения в списке записей.
        search_fields (tuple): Поля для поиска в панели администратора.
    """

    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name', 'ingredient__name',)

class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Админка для модели ShoppingCart.

    Атрибуты:
        list_display (tuple): Поля для отображения в списке записей.
        search_fields (tuple): Поля для поиска в панели администратора.
    """

    list_display = ('user', 'recipe')
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name',
    )

class FavoriteAdmin(admin.ModelAdmin):
    """
    Админка для модели Favorite.

    Атрибуты:
        list_display (tuple): Поля для отображения в списке записей.
        search_fields (tuple): Поля для поиска в панели администратора.
    """

    list_display = ('user', 'recipe')
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name',
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
