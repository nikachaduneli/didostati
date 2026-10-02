from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers as s


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
