# Generated by Django 4.1.7 on 2023-03-07 20:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('order', '0004_generate_delivery_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_num',
            field=models.CharField(max_length=40, unique=True,
                                   verbose_name='order number'),
        ),
        migrations.AddField(
            model_name='order',
            name='info',
            field=models.CharField(blank=True, max_length=150,
                                   verbose_name='miscellaneous info'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[('ip', 'In progress'), ('pp', 'Pending payment'),
                         ('@p', 'Processing payment'),
                         ('pf', 'Payment failed'), ('p', 'Paid'),
                         ('pr', 'Preparing'), ('ps', 'Pending shipping'),
                         ('it', 'In transit'), ('d', 'Delivered'),
                         ('cd', 'Completed'), ('rr', 'Return requested'),
                         ('ra', 'Return approved'), ('rd', 'Return denied'),
                         ('rt', 'Return in transit'), ('rn', 'Returned'),
                         ('v', 'Void'), ('c', 'Cancelled')], default='v',
                max_length=2, verbose_name='status'),
        ),
    ]