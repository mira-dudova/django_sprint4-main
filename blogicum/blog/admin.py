from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'slug')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'category',
        'location',
        'pub_date',
        'is_published',
        'created_at',
    )
    list_editable = ('is_published',)
    search_fields = ('title', 'author__username')
    list_filter = ('is_published', 'pub_date', 'category', 'location')
