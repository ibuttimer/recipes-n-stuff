# Generated by Django 4.1.5 on 2023-01-17 18:40

from django.db import migrations, models
import django.db.models.deletion
import utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_measure_base_metric_alter_measure_base_us'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measure',
            name='is_default',
            field=models.BooleanField(
                default=False,
                help_text='Designates the default measurement for the system '
                          'and type.'),
        ),
        migrations.AlterField(
            model_name='measure',
            name='system',
            field=models.CharField(
                choices=[
                    ('us', 'US'), ('si', 'Metric'), ('1', 'Dimensionless')
                ], default='us',
                help_text='Designates the measurement system.', max_length=2),
        ),
        migrations.AlterField(
            model_name='measure',
            name='type',
            field=models.CharField(
                choices=[
                    ('df', 'Dry/fluid'), ('w', 'Weight'), ('u', 'Unit')
                ], default='df',
                help_text='Designates the type of measurement.', max_length=2),
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id',
                 models.BigAutoField(
                     auto_created=True, primary_key=True, serialize=False,
                     verbose_name='ID')),
                ('name',
                 models.CharField(
                     max_length=75, unique=True, verbose_name='name')),
                ('measure',
                 models.ForeignKey(
                     help_text='Designates the standard measure for the '
                               'ingredient.',
                     on_delete=django.db.models.deletion.CASCADE,
                     to='recipes.measure')),
            ],
            bases=(utils.models.ModelMixin, models.Model),
        ),
    ]
