import json
import logging

from django.conf import settings
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, payments, serializers as s, services
from .emails import send_order_notification

logger = logging.getLogger(__name__)


class CartPrice(APIView):
    """Prices a client-side cart. Body: {"lines": [{product, color, size, quantity}]}"""

    def post(self, request):
        ser = s.CartLineInputSerializer(data=request.data.get('lines', []), many=True)
        ser.is_valid(raise_exception=True)
        lines, total = s.price_lines(ser.validated_data)
        for l in lines:
            l.pop('_product'), l.pop('_color'), l.pop('_size')
        return Response({'lines': lines, 'total': total})


class PaymentMethods(APIView):
    """Payment options offered at checkout."""

    def get(self, request):
        methods = [{'key': g.key, 'label': g.label} for g in payments.enabled_gateways()]
        if settings.PAYMENT_CASH_ON_DELIVERY:
            methods.append({'key': 'cod', 'label': 'Pay on delivery'})
        return Response(methods)


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
        provider = ser.validated_data['provider']
        order = ser.save()
        data = s.OrderSerializer(order, context={'request': request}).data
        if provider == 'cod':
            send_order_notification(order)
            return Response(data, status=status.HTTP_201_CREATED)
        lang = 'ka' if (request.headers.get('X-Lang') or '').startswith('ka') else 'en'
        try:
            data['payment_url'] = services.start_payment(order, payments.GATEWAYS[provider], request, lang)
        except payments.PaymentError:
            logger.exception('Could not start payment for order #%s', order.pk)
            models.Order.objects.filter(pk=order.pk).update(payment_status='failed')
            return Response({'detail': 'The payment service is unavailable right now. Please try again.'},
                            status=status.HTTP_502_BAD_GATEWAY)
        return Response(data, status=status.HTTP_201_CREATED)


class OrderPaymentStatus(APIView):
    """Where the customer lands after the bank's page. `token` comes from the return URL."""

    def get(self, request, token):
        order = services.order_from_token(token)
        if not order:
            return Response(status=status.HTTP_404_NOT_FOUND)
        services.sync_status(order)
        return Response(s.OrderSerializer(order, context={'request': request}).data)


class PaymentCallback(APIView):
    """The bank tells us a payment finished. The body is only a hint at which payment to look up."""
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, provider):
        gateway = payments.GATEWAYS.get(provider)
        if not gateway or not gateway.enabled():
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            data = json.loads(request.body or b'{}')
        except ValueError:
            data = {}
        payment_id = gateway.callback_payment_id(data) if isinstance(data, dict) else None
        order = models.Order.objects.filter(payment_provider=provider, payment_id=payment_id).first() if payment_id else None
        if order:
            services.sync_status(order)
        return Response(status=status.HTTP_200_OK)
