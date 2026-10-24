import secrets

from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def fill_numbers(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    used = set()
    for order in Order.objects.filter(number=''):
        day = timezone.localdate(order.created_at)
        while True:
            number = f'{settings.ORDER_NUMBER_PREFIX}-{day:%y%m%d}-{secrets.randbelow(90000) + 10000}'
            if number not in used:
                break
        used.add(number)
        Order.objects.filter(pk=order.pk).update(number=number)


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='number',
            field=models.CharField(default='', editable=False, max_length=30, verbose_name='order number'),
            preserve_default=False,
        ),
        migrations.RunPython(fill_numbers, migrations.RunPython.noop),
    ]
