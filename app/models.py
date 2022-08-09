from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser


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


class CustomUser(AbstractUser):
    user_id = models.CharField(max_length=25, primary_key=True, verbose_name="user_id")
    # location1 = models.CharField(max_length=50, verbose_name="よく行く場所１")

    def __str__(self):
        return self.user_id

class location(models.Model):
    user_id = models.ForeignKey(CustomUser, db_column='user_id', on_delete=models.CASCADE)
    location_name = models.CharField(max_length=50, verbose_name="よく行く場所")
    ido = models.FloatField(verbose_name="緯度")
    keido = models.FloatField(verbose_name="経度")