# Generated by Django 3.2.6 on 2021-08-19 22:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0022_plans_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plans',
            name='comment',
            field=models.CharField(max_length=255, verbose_name='comment'),
        ),
        migrations.AlterField(
            model_name='plans',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_at'),
        ),
        migrations.AlterField(
            model_name='plans',
            name='created_by',
            field=models.CharField(max_length=255, verbose_name='created_by'),
        ),
        migrations.AlterField(
            model_name='plans',
            name='image',
            field=models.ImageField(upload_to='images/', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='player',
            name='address',
            field=models.CharField(max_length=255, verbose_name='street_house number'),
        ),
        migrations.AlterField(
            model_name='player',
            name='city',
            field=models.CharField(max_length=255, verbose_name='city'),
        ),
        migrations.AlterField(
            model_name='player',
            name='date_of_birth',
            field=models.DateField(verbose_name='date_of_birth'),
        ),
        migrations.AlterField(
            model_name='player',
            name='email_address',
            field=models.EmailField(max_length=254, verbose_name='email_address'),
        ),
        migrations.AlterField(
            model_name='player',
            name='first_name',
            field=models.CharField(max_length=255, verbose_name='first_name'),
        ),
        migrations.AlterField(
            model_name='player',
            name='image',
            field=models.ImageField(blank=True, default='images/no_image.png', null=True, upload_to='images/', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='player',
            name='phone_number',
            field=models.CharField(default='0', max_length=255, verbose_name='phone_number'),
        ),
        migrations.AlterField(
            model_name='player',
            name='post_code',
            field=models.CharField(max_length=255, verbose_name='post_code'),
        ),
        migrations.AlterField(
            model_name='player',
            name='society',
            field=models.CharField(max_length=255, verbose_name='society'),
        ),
        migrations.AlterField(
            model_name='playerskills',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='players.player', verbose_name='player'),
        ),
        migrations.AlterField(
            model_name='playerskills',
            name='skill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='players.skills', verbose_name='skill'),
        ),
        migrations.AlterField(
            model_name='playerskills',
            name='value',
            field=models.IntegerField(default=0, verbose_name='value'),
        ),
    ]