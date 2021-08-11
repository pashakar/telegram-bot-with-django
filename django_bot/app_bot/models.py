from django.db import models


class DataUser(models.Model):
    username = models.CharField(max_length=128, verbose_name='Имя пользователя')
    tg_id = models.PositiveIntegerField(verbose_name='id пользователя', primary_key=True)
    count_hotels = models.PositiveIntegerField(verbose_name='количество отелей', null=True)
    distance = models.FloatField(verbose_name='расстояние от цента', null=True)
    destination_id = models.PositiveIntegerField(verbose_name='id города', null=True)
    sort_order = models.CharField(max_length=128, verbose_name="порядок сортировки", null=True)
    price_min = models.CharField(max_length=128, verbose_name='минимальная цена', null=True)
    price_max = models.CharField(max_length=128, verbose_name='максимальная цена', null=True)
    date_in = models.DateField(verbose_name='дата заезда', null=True)
    date_out = models.DateField(verbose_name='дата выезда', null=True)

    def __str__(self):
        return self.username
