# Generated by Django 2.2 on 2021-08-09 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_bot', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datauser',
            name='id',
        ),
        migrations.AlterField(
            model_name='datauser',
            name='tg_id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False, verbose_name='id пользователя'),
        ),
    ]
