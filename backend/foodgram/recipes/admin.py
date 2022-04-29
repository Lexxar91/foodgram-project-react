from django.contrib import admin
from .models import AmountIngredient, Ingredient, Recipe, Tag


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



class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)

class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(AmountIngredient, AmountIngredientAdmin)
