# Generated by Django 3.2.6 on 2021-08-22 07:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0028_alter_playerskills_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerskills',
            name='value',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='value'),
        ),
    ]
