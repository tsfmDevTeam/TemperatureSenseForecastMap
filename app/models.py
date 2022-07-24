from django.db import models


class AmedasPoint(models.Model):
    ido = models.FloatField(verbose_name="ido")
    keido = models.FloatField(verbose_name="keido")
    wgbt_24 = models.FloatField(verbose_name="wgbt_24")