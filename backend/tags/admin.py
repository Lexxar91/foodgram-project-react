from django.contrib import admin

from tags.models import Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)


admin.site.register(Tag, TagAdmin)
