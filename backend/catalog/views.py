from django.db.models import Count, Q
from rest_framework import generics
from core.cache import CachedResponseMixin
from . import models, serializers as s


class CategoryList(CachedResponseMixin, generics.ListAPIView):
    serializer_class = s.CategorySerializer
    pagination_class = None

    def get_queryset(self):
        return models.Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True)))


class ProductList(CachedResponseMixin, generics.ListAPIView):
    """Query params: category, search, popular, on_sale, min_price, max_price, ordering."""
    serializer_class = s.ProductListSerializer
    ORDERINGS = {'newest': '-created_at', 'price_asc': 'price', 'price_desc': '-price', 'name': 'name'}

    def get_queryset(self):
        qs = models.Product.objects.filter(is_active=True).select_related('category') \
            .prefetch_related('images', 'colors', 'sizes', 'bundle_items__product__images',
                         'bundle_items__product__colors', 'bundle_items__product__category')
        q = self.request.query_params
        if q.get('category'):
            qs = qs.filter(category__slug=q['category'])
        if q.get('search'):
            for word in q['search'].split():
                qs = qs.filter(Q(name__icontains=word) | Q(description__icontains=word)
                               | Q(name_ka__icontains=word) | Q(description_ka__icontains=word)
                               | Q(category__name__icontains=word) | Q(category__name_ka__icontains=word)
                               | Q(colors__name__icontains=word) | Q(colors__name_ka__icontains=word))
            qs = qs.distinct()
        if q.get('popular') in ('1', 'true'):
            qs = qs.filter(is_popular=True)
        if q.get('on_sale') in ('1', 'true'):
            qs = qs.filter(discount_percent__gt=0)
        for param, lookup in (('min_price', 'price__gte'), ('max_price', 'price__lte')):
            try:
                qs = qs.filter(**{lookup: float(q[param])}) if q.get(param) else qs
            except ValueError:
                pass
        return qs.order_by(self.ORDERINGS.get(q.get('ordering'), '-created_at'))

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('popular') in ('1', 'true'):
            return None  # main page shows all popular products unpaginated
        return super().paginate_queryset(queryset)


class ProductDetail(CachedResponseMixin, generics.RetrieveAPIView):
    serializer_class = s.ProductDetailSerializer
    lookup_field = 'slug'
    queryset = models.Product.objects.filter(is_active=True).select_related('category') \
        .prefetch_related('images', 'colors', 'sizes', 'bundle_items__product__images',
                         'bundle_items__product__colors', 'bundle_items__product__category')
