"""Card payment gateways: Bank of Georgia and TBC Bank.

Each gateway can start a payment (returning the bank's hosted payment page address) and look up the
final status of a payment. The status always comes from the bank's API, never from the data the
customer's browser or a callback body claims, so a forged request cannot mark an order as paid.
"""
import base64
import json
import urllib.error
import urllib.parse
import urllib.request
import uuid

from django.conf import settings
from django.core.cache import cache

from core import config

PAID, FAILED, PENDING = 'paid', 'failed', 'pending'


class PaymentError(Exception):
    """The bank could not be reached or refused the request."""


def http(method, url, headers=None, json_body=None, form=None, timeout=20):
    headers = dict(headers or {})
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers['Content-Type'] = 'application/json'
    elif form is not None:
        data = urllib.parse.urlencode(form).encode()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read() or b'{}')
    except urllib.error.HTTPError as e:
        raise PaymentError(f'{url} answered {e.code}: {e.read()[:300]!r}') from e
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise PaymentError(f'{url} failed: {e}') from e


class Gateway:
    key = ''
    label = ''

    def enabled(self):
        raise NotImplementedError

    def create(self, order, return_url, callback_url, lang):
        """Returns (payment_id, url the customer must be sent to)."""
        raise NotImplementedError

    def status(self, payment_id):
        """Returns PAID, FAILED or PENDING."""
        raise NotImplementedError

    def callback_payment_id(self, data):
        """Extracts the payment id from a callback body (it is only a hint: status() decides)."""
        raise NotImplementedError


class BankOfGeorgia(Gateway):
    key = 'bog'
    label = 'Bank of Georgia'
    base = 'https://api.bog.ge/payments/v1'
    token_url = 'https://oauth2.bog.ge/auth/realms/bog/protocol/openid-connect/token'

    def enabled(self):
        return bool(config.get('BOG_CLIENT_ID') and config.get('BOG_CLIENT_SECRET'))

    def _token(self):
        token = cache.get('bog_token')
        if not token:
            basic = base64.b64encode(f'{config.get('BOG_CLIENT_ID')}:{config.get('BOG_CLIENT_SECRET')}'.encode()).decode()
            res = http('POST', self.token_url, headers={'Authorization': f'Basic {basic}'},
                       form={'grant_type': 'client_credentials'})
            token = res['access_token']
            # Reuse for a few minutes; the bank's `expires_in` is not reliable enough to trust.
            cache.set('bog_token', token, 300)
        return token

    def _auth(self):
        return {'Authorization': f'Bearer {self._token()}'}

    def create(self, order, return_url, callback_url, lang):
        body = {
            'callback_url': callback_url,
            'external_order_id': str(order.pk),
            'redirect_urls': {'success': return_url, 'fail': return_url},
            'purchase_units': {
                'currency': 'GEL',
                'total_amount': float(order.total),
                'basket': [{'product_id': str(i.product_id or i.pk), 'description': i.product_name[:100],
                            'quantity': i.quantity, 'unit_price': float(i.unit_price)}
                           for i in order.items.all()],
            },
        }
        headers = {**self._auth(), 'Accept-Language': 'ka' if lang == 'ka' else 'en',
                   'Idempotency-Key': str(uuid.uuid4())}
        res = http('POST', f'{self.base}/ecommerce/orders', headers=headers, json_body=body)
        try:
            return res['id'], res['_links']['redirect']['href']
        except KeyError as e:
            raise PaymentError(f'Unexpected Bank of Georgia response: {res}') from e

    def status(self, payment_id):
        res = http('GET', f'{self.base}/receipt/{urllib.parse.quote(payment_id)}', headers=self._auth())
        key = (res.get('order_status') or {}).get('key')
        if key == 'completed':
            return PAID
        if key == 'rejected':
            return FAILED
        return PENDING

    def callback_payment_id(self, data):
        return (data.get('body') or {}).get('order_id')


class TBC(Gateway):
    key = 'tbc'
    label = 'TBC Bank'
    base = 'https://api.tbcbank.ge/v1/tpay'

    def enabled(self):
        return bool(config.get('TBC_API_KEY') and config.get('TBC_CLIENT_ID') and config.get('TBC_CLIENT_SECRET'))

    def _headers(self):
        token = cache.get('tbc_token')
        if not token:
            # The docs spell the field `client_id`, TBC's own samples `client_Id`: send both to be safe.
            res = http('POST', f'{self.base}/access-token', headers={'apikey': config.get('TBC_API_KEY')},
                       form={'client_id': config.get('TBC_CLIENT_ID'), 'client_Id': config.get('TBC_CLIENT_ID'),
                             'client_secret': config.get('TBC_CLIENT_SECRET')})
            token = res['access_token']
            cache.set('tbc_token', token, 3600)  # tokens last a day
        return {'apikey': config.get('TBC_API_KEY'), 'Authorization': f'Bearer {token}'}

    def create(self, order, return_url, callback_url, lang):
        body = {
            'amount': {'currency': 'GEL', 'total': float(order.total)},
            'returnurl': return_url,
            'callbackUrl': callback_url,
            'merchantPaymentId': str(order.pk),
            'description': f'Didostati order #{order.pk}'[:30],
            'language': 'KA' if lang == 'ka' else 'EN',
            'preAuth': False,
        }
        res = http('POST', f'{self.base}/payments', headers=self._headers(), json_body=body)
        url = next((l['uri'] for l in res.get('links', []) if l.get('rel') == 'approval_url'), None)
        if not res.get('payId') or not url:
            raise PaymentError(f'Unexpected TBC response: {res}')
        return res['payId'], url

    def status(self, payment_id):
        res = http('GET', f'{self.base}/payments/{urllib.parse.quote(payment_id)}', headers=self._headers())
        status = res.get('status')
        if status == 'Succeeded':
            return PAID
        if status in ('Failed', 'Expired'):
            return FAILED
        return PENDING

    def callback_payment_id(self, data):
        return data.get('PaymentId')


class Mock(Gateway):
    """Development stand-in: sends the customer straight back and reports the payment as successful."""
    key = 'mock'
    label = 'Test payment (development)'

    def enabled(self):
        return settings.PAYMENT_MOCK_ENABLED

    def create(self, order, return_url, callback_url, lang):
        return f'mock-{order.pk}', return_url

    def status(self, payment_id):
        return PAID

    def callback_payment_id(self, data):
        return data.get('payment_id')


GATEWAYS = {g.key: g for g in (BankOfGeorgia(), TBC(), Mock())}


def enabled_gateways():
    return [g for g in GATEWAYS.values() if g.enabled()]
