# Generated by Django 4.1.5 on 2023-02-14 11:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0010_recipeingredient_index'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instruction',
            options={'ordering': ['index']},
        ),
        migrations.AddField(
            model_name='instruction',
            name='index',
            field=models.PositiveSmallIntegerField(default=1, validators=[
                django.core.validators.MinValueValidator(1),
                django.core.validators.MaxValueValidator(32767)
            ],
            verbose_name='index in instruction list'),
        ),
    ]
