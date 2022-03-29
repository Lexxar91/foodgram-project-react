from django.contrib import admin
from users.models import User
from .models import Recipe

class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'first_name',
        'last_name',
        'email',
        'username',
        'password'
    )
    search_fields = ('email', 'usename',)

class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
    )
    readonly_fields = ('favorite_count',)
    list_filter = ('author', 'name', 'tags',)

    def favorite_count(self, obj):
        return obj.favorite_recipe.count()


admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)

