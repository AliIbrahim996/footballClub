# Generated by Django 3.2.6 on 2021-08-08 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0013_alter_player_date_of_birth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='date_of_birth',
            field=models.DateTimeField(default=(2021, 8, 8, 15, 34, 30, 6, 220, 1)),
        ),
    ]
