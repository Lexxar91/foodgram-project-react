from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'first_name',
        'last_name',
        'email',
        'username',
        'password'
    )
    search_fields = ('username', 'email', 'last_name',)
    list_filter = ('username', 'email', 'first_name', 'last_name',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    list_filter = ('user', 'author',)
    search_fields = ('user__username', 'user__email',)


admin.site.register(Follow, FollowAdmin)
admin.site.register(User, UserAdmin)
