from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import models


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0
    fields = ('product_name', 'color_name', 'size_name', 'unit_price', 'quantity', 'line_total')
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description=_('line total'))
    def line_total(self, obj):
        return obj.line_total


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'total', 'status', 'created_at')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'full_name', 'email', 'phone')
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    fieldsets = (
        (_('Order'), {'fields': ('status', 'total', 'created_at', 'user', 'note')}),
        (_('Customer'), {'fields': ('full_name', 'email', 'phone')}),
        (_('Delivery address'), {'fields': ('line1', 'line2', 'city', 'postal_code', 'country')}),
    )
    # Orders are records of what the customer bought: only the status can be changed.
    readonly_fields = ('total', 'created_at', 'user', 'note', 'full_name', 'email', 'phone',
                       'line1', 'line2', 'city', 'postal_code', 'country')

    def has_add_permission(self, request):
        return False
