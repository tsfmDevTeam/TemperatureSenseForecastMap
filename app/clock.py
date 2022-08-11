from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore,register_events,register_job
from .models import point_name
import json
from urllib import request
import time

from src import wgbt




def test_job():
    for point in point_name.objects.all():
        #更新
        ido = point.ido
        keido = point.keido

        wgbts_list, time_list = wgbt.location2wgbt(ido, keido)
        point.wgbts_list = wgbts_list
        point.time_list = time_list

        point.save() #ここでUPDATEが実行される
        time.sleep(1)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(test_job, 'cron', hour=0, minute=39)# 毎日23時59分に実行
    scheduler.start()