# Generated by Django 4.1.5 on 2023-01-25 15:10

from django.db import migrations

from ..permissions import (
    add_subs_permissions_for_registered,
    remove_subs_permissions_for_registered
)


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            add_subs_permissions_for_registered,
            remove_subs_permissions_for_registered),
    ]
