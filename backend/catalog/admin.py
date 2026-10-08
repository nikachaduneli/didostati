from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import DiscountForm
from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'thumb')
    list_editable = ('order',)
    readonly_fields = ('slug', 'image_display')

    def image_display(self, object):
        return mark_safe(f'<img src="{object.image.url}" height="400"/>')


    @admin.display(description=_('Picture'))
    def thumb(self, obj):
        return mark_safe(f'<img src="{obj.image.url}" height="40">') if obj.image else ''


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
    fields = ('image_display', 'image', 'color', 'order')
    readonly_fields = ('image_display',)

    @admin.display(description=_('Preview'))
    def image_display(self, object):
        return format_html('<img src="{}" height="100"/>', object.image.url) if object.image else '-'



class ProductSizeInline(admin.TabularInline):
    model = models.ProductSize
    extra = 0
    fields = ('name', 'name_ka', 'price', 'order')


class CollectionItemInline(admin.TabularInline):
    model = models.CollectionItem
    fk_name = 'collection'
    extra = 0
    autocomplete_fields = ('product',)
    verbose_name = _('product in this collection')
    verbose_name_plural = _('Collection contents (leave empty for a normal product)')


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_percent', 'is_popular', 'is_active')
    list_editable = ('discount_percent', 'is_popular', 'is_active')
    list_filter = ('category', 'is_popular', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('slug',)
    filter_horizontal = ('colors',)
    inlines = [ProductSizeInline, CollectionItemInline, ProductImageInline]


    actions = ['apply_discount']

    @admin.action(description=_("Apply bulk discount to selected products"))
    def apply_discount(self, request, queryset):
        if 'apply' in request.POST:
            form = DiscountForm(request.POST)

            if form.is_valid():
                discount = form.cleaned_data['discount_percentage']

                updated_count = queryset.count()
                for product in queryset:
                    product.discount_percent = discount
                    product.save()

                self.message_user(
                    request,
                    f"Successfully applied {discount}% discount to {updated_count} products.",
                    messages.SUCCESS
                )
                return HttpResponseRedirect(request.get_full_path())

        else: form = DiscountForm()

        return render(
            request,
            'admin/apply_discount.html',
            context={'form': form, 'queryset': queryset, 'title': 'Apply Bulk Discount'}
        )
