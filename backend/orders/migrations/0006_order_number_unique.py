from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_order_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='number',
            field=models.CharField(editable=False, help_text='Reference shown to the customer, e.g. DS-261024-48213.', max_length=30, unique=True, verbose_name='order number'),
        ),
    ]
