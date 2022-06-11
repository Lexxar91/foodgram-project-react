from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingCart)


class RecipeAdmin(admin.ModelAdmin):
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
        return obj.favorite_recipe.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('measurement_unit',)
    list_filter = ('measurement_unit',)


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name', 'ingredient__name',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = (
        'user__username',
        'user__email',
        'recipe__name',
    )


class FavoriteAdmin(admin.ModelAdmin):
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
