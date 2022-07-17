import json
from urllib import request


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

    with request.urlopen(url) as r:
        body = json.loads(r.read())

        tdate = body["current_weather"]["time"]
        index_now_time = body["hourly"]["time"].index(tdate)

        for index in range(index_now_time, index_now_time + 24):
            time = body["hourly"]["time"][index]
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


def wgbt_indicator(WBGT: float) -> str:
    """WGBT温度による熱中症リスクの診断

    Args:
        WBGT (float): WGBT温度

    Returns:
        message (str): 危険度合のメッセージ
    """
    status: list[str] = ["運動は原則中止", "厳重警戒（激しい運動は中止）", "警戒（積極的に休憩)", "注意（積極的に水分補給）", "ほぼ安全（適宜水分補給）"]

    if WBGT > 35:
        return status[0]
    elif 35 > WBGT >= 31:
        return status[1]
    elif 31 > WBGT >= 28:
        return status[2]
    elif 28 > WBGT >= 24:
        return status[3]
    else:  # WBGT < 24:
        return status[4]
