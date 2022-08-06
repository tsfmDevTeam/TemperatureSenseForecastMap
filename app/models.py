from django.db import models
from django.contrib.postgres.fields import ArrayField


class point_name(models.Model):

    name = models.CharField(max_length=31, verbose_name="地点名")
    katakana = models.CharField(max_length=31, verbose_name="カタカナ名")
    address = models.CharField(max_length=31, verbose_name="住所")
    ido = models.FloatField(verbose_name="緯度")
    keido = models.FloatField(verbose_name="経度")

    wgbt_list = ArrayField(
        models.CharField(max_length=10, null=True, blank=True),
        size=6,
        null=True,
        blank=True,
        max_length=25,
        verbose_name="24時間のwgbt")

    time_list = ArrayField(
        models.CharField(max_length=10, null=True, blank=True),
        size=6,
        null=True,
        blank=True,
        max_length=25,
        verbose_name="時間リスト")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "地点名"