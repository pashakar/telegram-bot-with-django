# Generated by Django 2.2 on 2021-08-10 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_bot', '0005_auto_20210810_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datauser',
            name='date_in',
            field=models.DateTimeField(null=True, verbose_name='дата заезда'),
        ),
    ]
