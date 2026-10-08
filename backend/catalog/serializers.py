from rest_framework import serializers

from core.serializers import ImageField, TranslatedMixin
from . import models


class CategorySerializer(TranslatedMixin, serializers.ModelSerializer):
    image = ImageField()
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Category
        fields = ('id', 'name', 'slug', 'image', 'description', 'product_count', 'order')
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


class SizeSerializer(TranslatedMixin, serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='effective_price', read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = models.ProductSize
        fields = ('id', 'name', 'price', 'final_price')
        translated = ('name',)


class ProductListSerializer(TranslatedMixin, serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    category_name = serializers.SerializerMethodField()
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    image = serializers.SerializerMethodField()
    colors = ColorSerializer(many=True, read_only=True)
    is_collection = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = ('id', 'name', 'slug', 'category', 'category_name', 'price', 'discount_percent',
                  'final_price', 'image', 'colors', 'is_popular', 'is_collection')
        translated = ('name',)

    def get_is_collection(self, obj):
        return bool(obj.bundle_items.all())  # uses prefetch

    def get_category_name(self, obj):
        return obj.category.tr('name')

    def get_image(self, obj):
        first = next(iter(self._all_images(obj)), None)
        return first.image.url if first else None

    @staticmethod
    def _all_images(obj):
        """A product's own pictures, followed by those of the products it contains (if a collection)."""
        images = list(obj.images.all())  # uses prefetch
        for item in obj.bundle_items.all():
            images.extend(item.product.images.all())
        return images


class CollectionItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = models.CollectionItem
        fields = ('quantity', 'product')


class ProductDetailSerializer(ProductListSerializer):
    images = serializers.SerializerMethodField()
    sizes = SizeSerializer(many=True, read_only=True)
    items = CollectionItemSerializer(source='bundle_items', many=True, read_only=True)
    items_total = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ('description', 'images', 'sizes', 'items', 'items_total')
        translated = ('name', 'description')

    def get_images(self, obj):
        own = {i.id for i in obj.images.all()}
        data = ProductImageSerializer(self._all_images(obj), many=True, context=self.context).data
        for row in data:
            if row['id'] not in own:
                row['color'] = None  # contained products' colours don't apply to the collection's picker
        return data

    def get_items_total(self, obj):
        """Price of the contents if bought separately (lets the shop show the saving)."""
        items = obj.bundle_items.all()
        return sum((i.product.final_price * i.quantity for i in items), 0) if items else None
