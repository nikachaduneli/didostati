from django.conf import settings
from django.db import transaction
from django.utils import translation

from rest_framework import serializers

from catalog.models import Product
from catalog.serializers import ColorSerializer, ProductListSerializer, SizeSerializer
from core import config
from . import models
from . import payments


class CartLineInputSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    color = serializers.IntegerField(required=False, allow_null=True)
    size = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, max_value=99)


def price_lines(raw_lines):
    """Resolve client cart lines against the DB. Prices always come from the server.

    Returns (lines, total); lines whose product is gone/inactive are dropped.
    """
    products = Product.objects.filter(
        is_active=True, pk__in=[l['product'] for l in raw_lines]
    ).prefetch_related('images', 'colors', 'sizes', 'bundle_items__product__images',
                         'bundle_items__product__colors', 'bundle_items__product__category')
    by_id = {p.pk: p for p in products}
    lines, total = [], 0
    for l in raw_lines:
        product = by_id.get(l['product'])
        if not product:
            continue
        color = None
        if l.get('color'):
            color = next((c for c in product.colors.all() if c.pk == l['color']), None)
            if color is None:
                raise serializers.ValidationError(f'Invalid colour for {product.name}.')
        elif product.colors.all():
            color = product.colors.all()[0]
        size = None
        if l.get('size'):
            size = next((x for x in product.sizes.all() if x.pk == l['size']), None)
            if size is None:
                raise serializers.ValidationError(f'Invalid size for {product.name}.')
        elif product.sizes.all():
            size = product.sizes.all()[0]
        unit_price = size.final_price if size else product.final_price
        line_total = unit_price * l['quantity']
        total += line_total
        lines.append({
            'product': ProductListSerializer(product).data,
            'color': ColorSerializer(color).data if color else None,
            'size': SizeSerializer(size).data if size else None,
            'quantity': l['quantity'],
            'unit_price': unit_price,
            'line_total': line_total,
            '_product': product, '_color': color, '_size': size,
        })
    return lines, total


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = models.OrderItem
        fields = ('product_name', 'color_name', 'size_name', 'unit_price', 'quantity', 'line_total')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    lines = CartLineInputSerializer(many=True, write_only=True)
    provider = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = models.Order
        fields = ('id', 'number', 'email', 'full_name', 'phone', 'line1', 'line2', 'city', 'postal_code',
                  'country', 'note', 'status', 'payment_status', 'total', 'created_at', 'items', 'lines', 'provider')
        read_only_fields = ('id', 'number', 'status', 'payment_status', 'total', 'created_at')

    def validate_lines(self, value):
        if not value:
            raise serializers.ValidationError('Your cart is empty.')
        return value

    def validate_provider(self, value):
        allowed = {g.key for g in payments.enabled_gateways()}
        if config.get('PAYMENT_CASH_ON_DELIVERY'):
            allowed.add('cod')
        if value not in allowed:
            raise serializers.ValidationError('Choose a payment method.')
        return value

    def validate(self, attrs):
        if 'provider' not in attrs:
            raise serializers.ValidationError({'provider': 'Choose a payment method.'})
        return attrs

    @transaction.atomic
    def create(self, validated):
        provider = validated.pop('provider')
        raw = validated.pop('lines')
        priced, total = price_lines(raw)
        if not priced:
            raise serializers.ValidationError({'lines': 'None of the products are available any more.'})
        request = self.context['request']
        user = request.user if request.user.is_authenticated else None
        lang = (translation.get_language() or '').split('-')[0]
        lang = lang if lang in dict(settings.LANGUAGES) else settings.LANGUAGE_CODE
        order = models.Order.objects.create(
            user=user, total=total, language=lang, payment_status='' if provider == 'cod' else 'pending', **validated)
        models.OrderItem.objects.bulk_create([
            models.OrderItem(order=order, product=l['_product'], product_name=l['_product'].name,
                             color_name=l['_color'].name if l['_color'] else '',
                             size_name=l['_size'].name if l['_size'] else '',
                             unit_price=l['unit_price'], quantity=l['quantity'])
            for l in priced
        ])
        return order
