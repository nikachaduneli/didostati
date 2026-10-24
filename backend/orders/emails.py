import logging

from django.core.mail import send_mail
from django.utils import translation
from django.utils.translation import gettext as _

from core import config

logger = logging.getLogger(__name__)

# The shop owner always reads order notifications in Georgian.
OWNER_LANGUAGE = 'ka'


def _sender():
    return config.get('DEFAULT_FROM_EMAIL') or config.get('SMTP_USER') or 'orders@didostati.local'


def _items_and_total(order, cur):
    lines = []
    for i in order.items.all():
        options = ', '.join(x for x in (i.color_name, i.size_name) if x)
        name = f'{i.product_name} ({options})' if options else i.product_name
        lines.append(f'  {i.quantity} x {name} @ {i.unit_price} {cur} = {i.line_total} {cur}')
    return [_('Items:'), *lines, '', _label(_('Total:'), f'{order.total} {cur}')]


def _label(label, value, indent=''):
    return f'{indent}{label} {value}'


def _address(order):
    return ', '.join(x for x in (order.line1, order.line2, order.city, order.postal_code, order.country) if x)


def send_order_notification(order):
    """Email the shop owner the details of a new order, then confirm it to the customer.

    Never raises: a mail problem must not fail checkout.
    """
    _notify_owner(order)
    send_order_confirmation(order)


def _notify_owner(order):
    recipient = config.get('ORDER_NOTIFICATION_EMAIL')
    if not recipient:
        return
    cur = config.get('ORDER_CURRENCY')
    with translation.override(OWNER_LANGUAGE):
        body = '\n'.join([
            _('New order %(number)s (%(date)s)') % {'number': order.number, 'date': f'{order.created_at:%Y-%m-%d %H:%M}'},
            '',
            *_items_and_total(order, cur),
            '',
            _('Customer:'),
            _label(_('Name:'), order.full_name, '  '),
            _label(_('Email:'), order.email, '  '),
            _label(_('Phone:'), order.phone, '  '),
            _label(_('Address:'), _address(order), '  '),
            _label(_('Account:'), order.user.email if order.user else _('guest'), '  '),
            _label(_('Language:'), order.get_language_display(), '  '),
            *(['', _label(_('Note:'), order.note)] if order.note else []),
        ])
        subject = _('New order %(number)s - %(total)s %(cur)s') % {'number': order.number, 'total': order.total, 'cur': cur}
    try:
        send_mail(subject, body, _sender(), [recipient])
    except Exception:
        logger.exception('Could not send notification for order %s', order.number)


def send_order_confirmation(order):
    """Email the customer a confirmation in the language they used on the site. Never raises."""
    if not order.email:
        return
    cur = config.get('ORDER_CURRENCY')
    with translation.override(order.language or OWNER_LANGUAGE):
        body = '\n'.join([
            _('Hello %(name)s,') % {'name': order.full_name},
            '',
            _('Thank you for your order! We have received order %(number)s and will contact you soon.')
            % {'number': order.number},
            '',
            *_items_and_total(order, cur),
            '',
            _label(_('Delivery address:'), _address(order)),
            _label(_('Phone:'), order.phone),
            *(['', _label(_('Note:'), order.note)] if order.note else []),
        ])
        subject = _('Your order %(number)s') % {'number': order.number}
    try:
        send_mail(subject, body, _sender(), [order.email])
    except Exception:
        logger.exception('Could not send confirmation for order %s', order.number)
