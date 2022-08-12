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

        print("id", point.id)
        print("地点名", point.name)
        print("ido", ido)
        print("keido", keido)

        try:
            wgbts_list, time_list, _ = wgbt.location2wgbt(ido, keido)

            # global wgbt_time_dict
            wgbt_time_dict = {}
            wgbt_time_dict["wgbt"] = wgbts_list
            wgbt_time_dict["time"] = time_list
            wgbt_time_json = json.dumps(wgbt_time_dict)

            print("wgbt_time_json", wgbt_time_json)
            point.wgbt_time_json = wgbt_time_json

            point.save() #ここでUPDATEが実行される
            time.sleep(1)
        except:
            print("止まりました")
            time.sleep(3)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(test_job, 'cron', hour=21, minute=51)# 毎日23時59分に実行
    scheduler.start()