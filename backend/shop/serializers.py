from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from . import models

User = get_user_model()


class ImageField(serializers.ImageField):
    """Return site-relative URLs so they work behind any proxy/host."""

    def to_representation(self, value):
        return value.url if value else None


class TranslatedMixin:
    """Swaps the fields listed in `Meta.translated` for their Georgian value when that language is active."""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in getattr(self.Meta, 'translated', ()):
            data[field] = instance.tr(field)
        return data


class CategorySerializer(TranslatedMixin, serializers.ModelSerializer):
    image = ImageField()
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Category
        fields = ('id', 'name', 'slug', 'image', 'description', 'product_count','order')
        translated = ('name', 'description')


class ColorSerializer(TranslatedMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Color
        fields = ('id', 'name', 'hex')
        translated = ('name',)


class ProductImageSerializer(serializers.ModelSerializer):
    image = ImageField()

    class Meta:
        model = models.ProductImage
        fields = ('id', 'image', 'color')


class ProductListSerializer(TranslatedMixin, serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    category_name = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    image = serializers.SerializerMethodField()
    colors = ColorSerializer(many=True, read_only=True)

    class Meta:
        model = models.Product
        fields = ('id', 'name', 'slug', 'category', 'category_name', 'price', 'discount_percent',
                  'final_price', 'image', 'colors', 'is_popular')
        translated = ('name',)

    def get_category_name(self, obj):
        return obj.category.tr('name')

    def get_image(self, obj):
        first = next(iter(obj.images.all()), None)  # uses prefetch
        return first.image.url if first else None


class ProductDetailSerializer(ProductListSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ('description', 'images')
        translated = ('name', 'description')


class PageSerializer(TranslatedMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Page
        fields = ('slug', 'title', 'content')
        translated = ('title', 'content')


class BlogListSerializer(TranslatedMixin, serializers.ModelSerializer):
    cover_image = ImageField()

    class Meta:
        model = models.Blog
        fields = ('id', 'title', 'slug', 'cover_image', 'excerpt', 'created_at')
        translated = ('title', 'excerpt')


class BlogDetailSerializer(BlogListSerializer):
    class Meta(BlogListSerializer.Meta):
        fields = BlogListSerializer.Meta.fields + ('content',)
        translated = ('title', 'excerpt', 'content')


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactMessage
        fields = ('name', 'email', 'message')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = ('id', 'label', 'full_name', 'phone', 'line1', 'line2', 'city',
                  'postal_code', 'country', 'is_default')


class CartLineInputSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    color = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, max_value=99)


def price_lines(raw_lines):
    """Resolve client cart lines against the DB. Prices always come from the server.

    Returns (lines, total); lines whose product is gone/inactive are dropped.
    """
    products = models.Product.objects.filter(
        is_active=True, pk__in=[l['product'] for l in raw_lines]
    ).prefetch_related('images', 'colors')
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name')


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=60, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated):
        return User.objects.create_user(username=validated['email'], email=validated['email'],
                                        first_name=validated.get('first_name', ''),
                                        password=validated['password'])
