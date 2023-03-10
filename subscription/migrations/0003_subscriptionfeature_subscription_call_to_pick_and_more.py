# Generated by Django 4.1.5 on 2023-01-26 14:37

from decimal import Decimal
from django.db import migrations, models
import utils.models


class Migration(migrations.Migration):
    dependencies = [
        ('subscription', '0002_alter_subscription_amount_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionFeature',
            fields=[
                ('id',
                 models.BigAutoField(auto_created=True, primary_key=True,
                                     serialize=False, verbose_name='ID')),
                ('description',
                 models.CharField(max_length=250, verbose_name='description')),
                ('feature_type', models.CharField(
                    choices=[('ba', 'Basic'), ('fd', 'Free delivery'),
                             ('fdo', 'Free delivery over'),
                             ('fda', 'Free delivery after'),
                             ('fc', 'Free classes'),
                             ('xif', 'First number of items free'),
                             ('fas', 'Free after spending')], default='ba',
                    max_length=3, verbose_name='feature type')),
                ('amount',
                 models.DecimalField(decimal_places=2, default=Decimal('0'),
                                     max_digits=19, verbose_name='amount')),
                ('base_currency', models.CharField(
                    default='EUR', max_length=3,
                    verbose_name='base currency')),
                ('count', models.IntegerField(
                    default=0, verbose_name='count')),
                ('is_active', models.BooleanField(
                    default=False, help_text='Designates that this record '
                                             'is active.',
                    verbose_name='is active')),
            ],
            bases=(utils.models.ModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='subscription',
            name='call_to_pick',
            field=models.CharField(default='Select', max_length=50,
                                   verbose_name='reason to pick'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='frequency_type',
            field=models.CharField(
                choices=[('dy', 'Daily'), ('wk', 'Weekly'), ('mt', 'Monthly'),
                         ('yr', 'Yearly')], default='mt', max_length=2,
                verbose_name='frequency type'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='features',
            field=models.ManyToManyField(
                to='subscription.subscriptionfeature'),
        ),
    ]
