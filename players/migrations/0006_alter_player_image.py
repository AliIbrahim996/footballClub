# Generated by Django 3.2.6 on 2021-08-08 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0005_alter_player_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='image',
            field=models.ImageField(blank=True, default='images/no_image.png', null=True, upload_to='images/ '),
        ),
    ]