# Generated by Django 3.2.6 on 2021-08-21 06:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0026_alter_category_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Category_model'},
        ),
        migrations.AlterModelOptions(
            name='plans',
            options={'verbose_name': 'Plans_model'},
        ),
        migrations.AlterModelOptions(
            name='player',
            options={'verbose_name': 'Player_model'},
        ),
        migrations.AlterModelOptions(
            name='playerskills',
            options={'verbose_name': 'Player_Skills_model'},
        ),
        migrations.AlterModelOptions(
            name='skills',
            options={'verbose_name': 'Skills_model'},
        ),
    ]
