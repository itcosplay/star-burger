from django.db import models
from django.utils import timezone


class Coordinates(models.Model):
    address = models.CharField (
        max_length=100,
        verbose_name='адрес'
    )

    lat = models.FloatField (
        default=None,
        null=True,
        verbose_name='широта'
    )

    lon = models.FloatField (
        default=None,
        null=True,
        verbose_name='долгота'
    )

    request_date = models.DateTimeField (
        default=timezone.now,
        verbose_name='дата запроса'
    )

    class Meta:
        verbose_name = 'координаты'
        verbose_name_plural = 'координаты'

    def __str__(self):
        return f'{self.address} ({self.lat} {self.lon})'
