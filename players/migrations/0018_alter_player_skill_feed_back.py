# Generated by Django 3.2.6 on 2021-08-12 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0017_player_skill_feed_back'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player_skill',
            name='feed_back',
            field=models.CharField(max_length=255),
        ),
    ]
