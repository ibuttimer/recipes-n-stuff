# Generated by Django 4.1.7 on 2023-03-11 15:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_create_order_through_relationships'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='items',
        ),
    ]
