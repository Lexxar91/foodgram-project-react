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
    search_fields = ('email', 'usename',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(Follow, FollowAdmin)
admin.site.register(User, UserAdmin)