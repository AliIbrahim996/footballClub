# Generated by Django 3.2.6 on 2021-08-16 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0021_auto_20210815_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='plans',
            name='comment',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
