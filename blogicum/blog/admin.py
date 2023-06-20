from django.contrib import admin
from django.utils import timezone

from .models import Category, Post, Location

admin.site.empty_value_display = 'Не задано'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at',
    )
    list_editable = (
        'category',
        'text',
    )
    search_fields = ('title',)
    list_fields = ('is_published',)
    list_filter = ('created_at',)
    list_display_links = ('title',)

    def is_published(self, obj):
        return obj.pub_date <= timezone.now()
    is_published.boolean = True
    is_published.short_description = 'Опубликована'


admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(Location)
