# Generated by Django 3.2.6 on 2021-08-08 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0011_alter_player_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='date_of_birth',
            field=models.DateTimeField(),
        ),
    ]
