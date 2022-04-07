from django.contrib import admin
from .models import User

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

admin.site.register(User, UserAdmin)