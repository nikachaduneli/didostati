import logging
from urllib.parse import quote

from django.core import signing
from django.db import transaction

from core import config
from . import payments
from .emails import send_order_notification
from .models import Order

logger = logging.getLogger(__name__)
SALT = 'order-return'


def order_token(order):
    """Unguessable reference placed in the return URL so the customer can see their own order status."""
    return signing.dumps(order.pk, salt=SALT)


def order_from_token(token):
    try:
        return Order.objects.get(pk=signing.loads(token, salt=SALT, max_age=7 * 24 * 3600))
    except (signing.BadSignature, Order.DoesNotExist):
        return None


def site_url(request):
    return (config.get('SITE_URL') or request.build_absolute_uri('/')).rstrip('/')


def start_payment(order, gateway, request, lang):
    """Registers the payment with the bank; returns the address of the bank's payment page."""
    base = site_url(request)
    return_url = f'{base}/payment/return?order={quote(order_token(order))}'
    callback_url = f'{base}/api/payments/{gateway.key}/callback/'
    payment_id, url = gateway.create(order, return_url, callback_url, lang)
    Order.objects.filter(pk=order.pk).update(payment_provider=gateway.key, payment_id=payment_id)
    order.payment_provider, order.payment_id = gateway.key, payment_id
    return url


def apply_status(order, status):
    """Idempotent: the shop owner is emailed once, however many times the bank reports success."""
    if status == payments.PAID:
        changed = Order.objects.filter(pk=order.pk).exclude(payment_status='paid').update(payment_status='paid')
        if changed:
            order.payment_status = 'paid'
            transaction.on_commit(lambda: send_order_notification(Order.objects.get(pk=order.pk)))
    elif status == payments.FAILED:
        # A payment that already succeeded is never downgraded.
        Order.objects.filter(pk=order.pk, payment_status='pending').update(payment_status='failed')
        if order.payment_status == 'pending':
            order.payment_status = 'failed'


def sync_status(order):
    """Asks the bank for the payment's final status while the order is still unpaid."""
    gateway = payments.GATEWAYS.get(order.payment_provider)
    if gateway and order.payment_id and order.payment_status != 'paid':
        try:
            apply_status(order, gateway.status(order.payment_id))
        except payments.PaymentError:
            logger.exception('Could not check payment %s of order #%s', order.payment_id, order.pk)
    return order
