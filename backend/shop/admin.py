from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from . import models

admin.site.site_header = _('Didostati administration')
admin.site.site_title = 'Didostati'


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'thumb')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description=_('Picture'))
    def thumb(self, obj):
        return format_html('<img src="{}" height="40">', obj.image.url) if obj.image else ''


@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex', 'swatch')

    @admin.display(description=_('Swatch'))
    def swatch(self, obj):
        return format_html('<span style="display:inline-block;width:24px;height:16px;'
                           'border:1px solid #888;background:{}"></span>', obj.hex)


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 2


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_percent', 'is_popular', 'is_active')
    list_editable = ('discount_percent', 'is_popular', 'is_active')
    list_filter = ('category', 'is_popular', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('colors',)
    inlines = [ProductImageInline]


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'updated_at')


@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_filter = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}


@admin.register(models.ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    readonly_fields = ('name', 'email', 'message', 'created_at')


@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'full_name', 'city')


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'color_name', 'unit_price', 'quantity')
    can_delete = False


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'total', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = ('full_name', 'email', 'phone')
    inlines = [OrderItemInline]
