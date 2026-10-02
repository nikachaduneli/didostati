from django.contrib import admin

from . import models


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
