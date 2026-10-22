from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_orderitem_size_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='payment ID'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_provider',
            field=models.CharField(blank=True, help_text='Empty = pay on delivery.', max_length=20, verbose_name='payment method'),
        ),
        # Orders placed before online payments existed have no payment status ('' = pay on delivery).
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(blank=True, default='', max_length=10, verbose_name='payment status'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(blank=True, choices=[('pending', 'Awaiting payment'), ('paid', 'Paid'), ('failed', 'Payment failed')], default='pending', max_length=10, verbose_name='payment status'),
        ),
    ]
