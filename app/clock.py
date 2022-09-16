import os
import time

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

from . import db2geojson, wbgt_util
from .models import point_name


def test_job():
    for point in point_name.objects.all():
        # 更新
        ido = point.ido
        keido = point.keido

        print("id:{} 地点名:{}".format(point.id, point.name))
        # print("ido", ido)
        # print("keido", keido)

        try:
            wbgts_list, time_list = wbgt_util.location2wbgt(ido, keido, hours=48)

            # global wbgt_time_dict
            wbgt_time_dict = {}
            wbgt_time_dict["wbgt"] = wbgts_list
            wbgt_time_dict["time"] = time_list
            wbgt_time_json = wbgt_time_dict

            # print("wbgt_time_json", wbgt_time_json)
            point.wbgt_time_json = wbgt_time_json

            point.save()  # ここでUPDATEが実行される
            time.sleep(1)

        except:
            print("id{}のDBの更新ができませんでした".format(point.id))
            time.sleep(3)
    db2geojson.data2geojson(force=True)


def sample():
    print("Hello")


def start():
    db2geojson.data2geojson()

    scheduler = BackgroundScheduler()
    hour, minute = map(int, os.environ.get("CLOCK_TIME", "00:00").split(":"))
    scheduler.add_job(test_job, "cron", hour=hour, minute=minute)  # 毎日23時59分に実行
    scheduler.start()
