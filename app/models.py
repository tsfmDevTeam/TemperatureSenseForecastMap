from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser


class point_name(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
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

    def __int__(self):
        return self.id

    class Meta:
        verbose_name_plural = "地点id"


class CustomUser(AbstractUser):
    pass

class location(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=50, verbose_name="よく行く場所")
    ido = models.FloatField(verbose_name="緯度")
    keido = models.FloatField(verbose_name="経度")

    class Meta:
        verbose_name_plural = "よく行く場所"