from django.db import transaction
from rest_framework import serializers

from catalog.models import Product
from catalog.serializers import ColorSerializer, ProductListSerializer
from . import models


class CartLineInputSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    color = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, max_value=99)


def price_lines(raw_lines):
    """Resolve client cart lines against the DB. Prices always come from the server.

    Returns (lines, total); lines whose product is gone/inactive are dropped.
    """
    products = Product.objects.filter(
        is_active=True, pk__in=[l['product'] for l in raw_lines]
    ).prefetch_related('images', 'colors', 'bundle_items__product__images',
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
        line_total = product.final_price * l['quantity']
        total += line_total
        lines.append({
            'product': ProductListSerializer(product).data,
            'color': ColorSerializer(color).data if color else None,
            'quantity': l['quantity'],
            'unit_price': product.final_price,
            'line_total': line_total,
            '_product': product, '_color': color,
        })
    return lines, total


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = models.OrderItem
        fields = ('product_name', 'color_name', 'unit_price', 'quantity', 'line_total')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    lines = CartLineInputSerializer(many=True, write_only=True)

    class Meta:
        model = models.Order
        fields = ('id', 'email', 'full_name', 'phone', 'line1', 'line2', 'city', 'postal_code',
                  'country', 'note', 'status', 'total', 'created_at', 'items', 'lines')
        read_only_fields = ('id', 'status', 'total', 'created_at')

    def validate_lines(self, value):
        if not value:
            raise serializers.ValidationError('Your cart is empty.')
        return value

    @transaction.atomic
    def create(self, validated):
        raw = validated.pop('lines')
        priced, total = price_lines(raw)
        if not priced:
            raise serializers.ValidationError({'lines': 'None of the products are available any more.'})
        request = self.context['request']
        user = request.user if request.user.is_authenticated else None
        order = models.Order.objects.create(user=user, total=total, **validated)
        models.OrderItem.objects.bulk_create([
            models.OrderItem(order=order, product=l['_product'], product_name=l['_product'].name,
                             color_name=l['_color'].name if l['_color'] else '',
                             unit_price=l['unit_price'], quantity=l['quantity'])
            for l in priced
        ])
        return order
