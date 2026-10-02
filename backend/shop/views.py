from django.contrib.auth import authenticate
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers as s


class CategoryList(generics.ListAPIView):
    serializer_class = s.CategorySerializer
    pagination_class = None

    def get_queryset(self):
        return models.Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True)))


class ProductList(generics.ListAPIView):
    """Query params: category, search, popular, on_sale, min_price, max_price, ordering."""
    serializer_class = s.ProductListSerializer
    ORDERINGS = {'newest': '-created_at', 'price_asc': 'price', 'price_desc': '-price', 'name': 'name'}

    def get_queryset(self):
        qs = models.Product.objects.filter(is_active=True).select_related('category') \
            .prefetch_related('images', 'colors')
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


class ProductDetail(generics.RetrieveAPIView):
    serializer_class = s.ProductDetailSerializer
    lookup_field = 'slug'
    queryset = models.Product.objects.filter(is_active=True).select_related('category') \
        .prefetch_related('images', 'colors')


class PageDetail(generics.RetrieveAPIView):
    serializer_class = s.PageSerializer
    lookup_field = 'slug'
    queryset = models.Page.objects.all()


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'
    queryset = models.Blog.objects.filter(is_published=True)

    def get_serializer_class(self):
        return s.BlogDetailSerializer if self.action == 'retrieve' else s.BlogListSerializer

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('limit'):
            return None
        return super().paginate_queryset(queryset)

    def filter_queryset(self, queryset):
        limit = self.request.query_params.get('limit')
        return queryset[:int(limit)] if limit and limit.isdigit() else queryset


class ContactCreate(generics.CreateAPIView):
    serializer_class = s.ContactMessageSerializer


class CartPrice(APIView):
    """Prices a client-side cart. Body: {"lines": [{product, color, quantity}]}"""

    def post(self, request):
        ser = s.CartLineInputSerializer(data=request.data.get('lines', []), many=True)
        ser.is_valid(raise_exception=True)
        lines, total = s.price_lines(ser.validated_data)
        for l in lines:
            l.pop('_product'), l.pop('_color')
        return Response({'lines': lines, 'total': total})


class OrderViewSet(viewsets.GenericViewSet):
    serializer_class = s.OrderSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def list(self, request):
        qs = models.Order.objects.filter(user=request.user).prefetch_related('items')
        return Response(self.get_serializer(qs, many=True).data)

    def create(self, request):  # guests allowed
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order = ser.save()
        return Response(s.OrderSerializer(order, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = s.AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return models.Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        first = not self.get_queryset().exists()
        serializer.save(user=self.request.user, **({'is_default': True} if first else {}))


def auth_response(user):
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': s.UserSerializer(user).data})


class Register(APIView):
    def post(self, request):
        ser = s.RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        return auth_response(ser.save())


class Login(APIView):
    def post(self, request):
        user = authenticate(username=str(request.data.get('email', '')).lower(),
                            password=request.data.get('password', ''))
        if not user:
            return Response({'detail': 'Wrong email or password.'}, status=status.HTTP_400_BAD_REQUEST)
        return auth_response(user)


class Me(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(s.UserSerializer(request.user).data)

    def delete(self, request):  # logout
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def spa(request, path=''):
    """Serve the built Vue app (run `npm run build` in /frontend)."""
    index = settings.BASE_DIR.parent / 'frontend' / 'dist' / 'index.html'
    if not index.exists():
        raise Http404('Frontend not built. Run "npm run dev" in /frontend, or "npm run build".')
    return FileResponse(open(index, 'rb'), content_type='text/html')
