import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_order_notification(order):
    """Email the shop owner the details of a new order. Never raises: a mail problem must not fail checkout."""
    recipient = settings.ORDER_NOTIFICATION_EMAIL
    if not recipient:
        return
    cur = settings.ORDER_CURRENCY
    lines = []
    for i in order.items.all():
        options = ', '.join(x for x in (i.color_name, i.size_name) if x)
        name = f'{i.product_name} ({options})' if options else i.product_name
        lines.append(f'  {i.quantity} x {name} @ {i.unit_price} {cur} = {i.line_total} {cur}')
    address = ', '.join(x for x in (order.line1, order.line2, order.city, order.postal_code, order.country) if x)
    body = '\n'.join([
        f'New order #{order.pk} ({order.created_at:%Y-%m-%d %H:%M})',
        '',
        'Items:', *lines,
        '',
        f'Total: {order.total} {cur}',
        '',
        'Customer:',
        f'  Name: {order.full_name}',
        f'  Email: {order.email}',
        f'  Phone: {order.phone}',
        f'  Address: {address}',
        f'  Account: {order.user.email if order.user else "guest"}',
        *(['', f'Note: {order.note}'] if order.note else []),
    ])
    try:
        send_mail(f'New order #{order.pk} - {order.total} {cur}', body, None, [recipient])
    except Exception:
        logger.exception('Could not send notification for order #%s', order.pk)
