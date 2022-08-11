from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore,register_events,register_job
from .models import point_name
import json
from urllib import request
import time


def location2wgbt(ido: float, keido: float) -> tuple[list[float], list[str]]:
    """WGBT温度の計算
    緯度・経度を用いて，Open-Meteo API(open-meteo.com)から，
        - 温度
        - 湿度
        - 直達日射量
        - 散乱日射量
        - 風速
        を取得します
        これらの値からWGBT温度を計算します
        (https://blog.obniz.com/news/obniz-wbgt-service.html)
    Args:
        - ido (float): 緯度
        - keido (float): 経度
    Returns:
        - wgbt (float): WGBT温度
    """

    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={ido}&longitude={keido}"
        "&hourly=temperature_2m,relativehumidity_2m,direct_radiation,diffuse_radiation,"
        "windspeed_10m&current_weather=true&timezone=Asia%2FTokyo"
    )

    wgbts_list: list[float] = []
    time_list: list[str] = []
    year = "2022-"
    str1 = "-"
    str2 = "T"

    with request.urlopen(url) as r:
        body = json.loads(r.read())

        tdate = body["current_weather"]["time"]
        index_now_time = body["hourly"]["time"].index(tdate)

        for index in range(index_now_time, index_now_time + 24):
            time = body["hourly"]["time"][index]

            time = time.replace(year, "")
            time = time.replace(str1, "月")
            time = time.replace(str2, "日")

            time_list.append(time)

            temperature = body["hourly"]["temperature_2m"][index]
            humidity = body["hourly"]["relativehumidity_2m"][index]
            direct_radiation = body["hourly"]["direct_radiation"][index] / 1000
            diffuse_radiation = body["hourly"]["diffuse_radiation"][index] / 1000
            windspeed_10m = abs(body["hourly"]["windspeed_10m"][index] * 1000 / 3600)

            wgbt = (
                    0.735 * temperature
                    + 0.0374 * humidity
                    + 0.00292 * temperature * humidity
                    + 7.619 * (direct_radiation + diffuse_radiation)
                    - 4.557 * (direct_radiation + diffuse_radiation) ** 2
                    - 0.0572 * windspeed_10m
                    - 4.064
            )
            wgbts_list.append(round(wgbt, 3))

    # 現在から24時間後の暑さ指数の予測値と時刻が入った配列
    return wgbts_list, time_list




def update_point_wgbt():
    for point in point_name.objects.all():
        #更新
        ido = point.ido
        keido = point.keido

        wgbts_list, time_list = location2wgbt(ido, keido)
        point.wgbts_list = wgbts_list
        point.time_list = time_list

        point.save() #ここでUPDATEが実行される
        time.sleep(1)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_point_wgbt, 'cron', hour=15, minute=10)# 毎日15時10分に実行
    scheduler.start()