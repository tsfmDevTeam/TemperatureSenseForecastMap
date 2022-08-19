from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore,register_events,register_job
from .models import point_name
import json
from urllib import request
import time

from src import wbgt




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
            wbgts_list, time_list, _ = wbgt.location2wbgt(ido, keido)

            # global wbgt_time_dict
            wbgt_time_dict = {}
            wbgt_time_dict["wbgt"] = wbgts_list
            wbgt_time_dict["time"] = time_list
            wbgt_time_json = json.dumps(wbgt_time_dict)

            print("wbgt_time_json", wbgt_time_json)
            point.wbgt_time_json = wbgt_time_json

            point.save() #ここでUPDATEが実行される
            time.sleep(1)
        except:
            print("id{}のDBの更新ができませんでした".format(point.id))
            time.sleep(3)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(test_job, 'cron', hour=0, minute=58)# 毎日23時59分に実行
    scheduler.start()