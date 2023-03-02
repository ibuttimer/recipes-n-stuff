# Generated by Django 4.1.5 on 2023-01-30 07:31

from django.db import migrations, models
import utils.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True, primary_key=True,
                                     serialize=False, verbose_name='ID')),
                ('code',
                 models.CharField(max_length=3, verbose_name='currency code')),
                ('numeric_code',
                 models.IntegerField(default=0, verbose_name='numeric code')),
                ('digits',
                 models.IntegerField(default=2,
                                     verbose_name='number of digits')),
                ('name', models.CharField(max_length=100,
                                          verbose_name='currency name')),
                ('symbol', models.CharField(default='¤', max_length=10,
                                            verbose_name='currency symbol')),
            ],
            bases=(utils.models.ModelMixin, models.Model),
        ),
    ]
