from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from catalog.models import Product
from core.models import AddressFields


class Order(AddressFields):
    STATUSES = [('new', _('New')), ('processing', _('Processing')), ('shipped', _('Shipped')),
                ('delivered', _('Delivered')), ('cancelled', _('Cancelled'))]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.SET_NULL, related_name='orders')
    email = models.EmailField(_('email'))
    note = models.TextField(_('note'), blank=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUSES, default='new')
    total = models.DecimalField(_('total'), max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return f'Order #{self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    product_name = models.CharField(_('product name'), max_length=200)
    color_name = models.CharField(_('colour'), max_length=60, blank=True)
    size_name = models.CharField(_('size'), max_length=60, blank=True)
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_('quantity'), default=1)

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')

    def __str__(self):
        options = ', '.join(x for x in (self.color_name, self.size_name) if x)
        return f'{self.quantity} × {self.product_name}' + (f' ({options})' if options else '')

    @property
    def line_total(self):
        return self.unit_price * self.quantity
