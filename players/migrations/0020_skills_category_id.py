# Generated by Django 3.2.6 on 2021-08-15 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0019_auto_20210815_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='skills',
            name='category_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='players.category'),
            preserve_default=False,
        ),
    ]
