from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientsInRecipe, Recipe,
                     ShoppingCart)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    search_fields = ('name',)
    readonly_fields = ('favorite_count',)
    list_filter = ('author', 'name', 'tags',)
    
    def favorite_count(self, obj):
        return obj.favorite_recipe.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
