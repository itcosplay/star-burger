# Generated by Django 3.2 on 2022-03-14 13:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20220312_0835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='quantity',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(25)], verbose_name='количество'),
        ),
    ]
