from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'slug', 'show_in_menu', 'ordering', 'updated_at')
    list_editable = ('show_in_menu', 'ordering')
    list_filter = ('show_in_menu',)
    fields = ('title', 'title_ka', 'slug', 'parent', 'show_in_menu', 'ordering', 'content', 'content_ka')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            kwargs['queryset'] = models.Page.objects.filter(parent=None)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'created_at')
    list_filter = ('is_published',)
    readonly_fields = ('slug',)


@admin.register(models.ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    readonly_fields = ('name', 'email', 'message', 'created_at')


@admin.register(models.Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('preview', '__str__', 'order', 'is_active')
    list_display_links = ('preview', '__str__')
    list_editable = ('order', 'is_active')
    readonly_fields = ('preview_large',)

    @admin.display(description='image')
    def preview(self, obj):
        return format_html('<img src="{}" style="height:60px;border-radius:6px">', obj.image.url) if obj.image else '-'

    @admin.display(description='preview')
    def preview_large(self, obj):
        return format_html('<img src="{}" style="max-width:600px;width:100%;border-radius:8px">', obj.image.url) if obj.image else '-'

    fields = ('image', 'preview_large', 'title', 'title_ka', 'subtitle', 'subtitle_ka', 'link', 'order', 'is_active')



@admin.register(models.Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', 'link', 'order', 'is_active')
    list_display_links = ('logo_preview', 'name')
    list_editable = ('order', 'is_active')

    @admin.display(description=_('logo'))
    def logo_preview(self, obj):
        return format_html('<img src="{}" style="height:40px">', obj.logo.url) if obj.logo else '-'
