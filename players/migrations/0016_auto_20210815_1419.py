# Generated by Django 3.2.6 on 2021-08-15 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0015_alter_player_date_of_birth'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterField(
            model_name='player',
            name='address',
            field=models.CharField(max_length=255, verbose_name='Straße_Hausnummer'),
        ),
        migrations.AlterField(
            model_name='player',
            name='city',
            field=models.CharField(max_length=255, verbose_name='stadt'),
        ),
        migrations.AlterField(
            model_name='player',
            name='date_of_birth',
            field=models.DateField(verbose_name='geburtstag'),
        ),
        migrations.AlterField(
            model_name='player',
            name='email_address',
            field=models.EmailField(max_length=254, verbose_name='emailadresse'),
        ),
        migrations.AlterField(
            model_name='player',
            name='first_name',
            field=models.CharField(max_length=255, verbose_name='vorname'),
        ),
        migrations.AlterField(
            model_name='player',
            name='name',
            field=models.CharField(max_length=255, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='player',
            name='phone_number',
            field=models.CharField(default='0', max_length=255, verbose_name='telefonnummer'),
        ),
        migrations.AlterField(
            model_name='player',
            name='post_code',
            field=models.CharField(max_length=255, verbose_name='postleitzahl'),
        ),
        migrations.AlterField(
            model_name='player',
            name='society',
            field=models.CharField(max_length=255, verbose_name='verein'),
        ),
    ]