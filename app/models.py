from django.contrib.auth.models import AbstractUser
from django.db import models


class point_name(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")
    name = models.CharField(max_length=31, verbose_name="地点名")
    katakana = models.CharField(max_length=31, verbose_name="カタカナ名")
    address = models.CharField(max_length=31, verbose_name="住所")
    ido = models.FloatField(verbose_name="緯度")
    keido = models.FloatField(verbose_name="経度")
    wbgt_time_json = models.JSONField(blank=True, null=True, verbose_name="24時間分のwbgt")

    def __int__(self):
        return self.id

    class Meta:
        verbose_name_plural = "地点id"


class CustomUser(AbstractUser):
    pass


class location(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=50, verbose_name="よく行く場所")
    # ido = models.FloatField(verbose_name="緯度")
    # keido = models.FloatField(verbose_name="経度")
    location_id = models.IntegerField(verbose_name="ロケーションID")
    kansokujo_name = models.CharField(max_length=31, verbose_name="登録した観測所名")

    class Meta:
        verbose_name_plural = "よく行く場所"
