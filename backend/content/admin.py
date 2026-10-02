from django.contrib import admin

from . import models


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'updated_at')


@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_filter = ('is_published',)
    readonly_fields = ('slug',)


@admin.register(models.ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    readonly_fields = ('name', 'email', 'message', 'created_at')
