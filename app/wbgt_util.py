import base64
import json
import os
import pathlib
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import BytesIO
from urllib import request

import matplotlib
import numpy as np
from matplotlib import pyplot as plt

matplotlib.use("Agg")


@dataclass
class wbgt_levels:
    level: int
    message: str
    min: int
    max: int
    color: str


wbgt_status: dict[int, wbgt_levels] = {
    1: wbgt_levels(level=1, message="ほぼ安全（適宜水分補給）", min=-100, max=24, color="#1C75BC"),
    2: wbgt_levels(level=2, message="注意（積極的に水分補給）", min=24, max=28, color="#16C4FD"),
    3: wbgt_levels(level=3, message="警戒（積極的に休憩)", min=28, max=31, color="#FFB23B"),
    4: wbgt_levels(level=4, message="厳重警戒（激しい運動は中止）", min=31, max=35, color="#F17816"),
    5: wbgt_levels(level=5, message="運動は原則中止", min=35, max=100, color="#FF5722"),
}


# プロットしたグラフを画像データとして出力するための関数
def output_graph():
    buffer = BytesIO()  # バイナリI/O(画像や音声データを取り扱う際に利用)
    plt.savefig(buffer, format="png")  # png形式の画像データを取り扱う
    buffer.seek(0)  # ストリーム先頭のoffset byteに変更
    img = buffer.getvalue()  # バッファの全内容を含むbytes
    graph = base64.b64encode(img)  # 画像ファイルをbase64でエンコード
    graph = graph.decode("utf-8")  # デコードして文字列から画像に変換
    buffer.close()
    return graph


def load_font():
    target = pathlib.Path(__file__).parent / "font.ttf"
    url = "https://github.com/minoryorg/Noto-Sans-CJK-JP/blob/master/fonts/NotoSansCJKjp-Regular.ttf?raw=true"

    if not target.exists():
        data = request.urlopen(url).read()
        with open(target, mode="wb") as f:
            f.write(data)


# グラフをプロットするための関数
def plot_graph(time_list: list[str], wbgt_list: list[float]):
    load_font()

    # plt.switch_backend("AGG")  # スクリプトを出力させない
    plt.figure(figsize=(10, 5))  # グラフサイズ
    graph_min = min(wbgt_list) // 1 - 1
    graph_max = max(wbgt_list) // 1 + 2

    virtual_x = list(range(len(time_list)))
    plt.ylim(graph_min, graph_max)
    plt.xlim(time_list[0], time_list[-1])

    alpha = 0.7
    levels = [np.empty(0), np.empty(0), np.empty(0), np.empty(0), np.empty(0)]
    full_detailed_x = [np.empty(0)]

    for x1, x2, y1, y2 in zip(virtual_x[:-1], virtual_x[1:], wbgt_list[:-1], wbgt_list[1:]):
        # print(f"{x1}, {x2}, {y1}, {y2}")

        def f(x):
            a = (y2 - y1) / (x2 - x1)
            b = y1 - a * x1
            return a * x + b

        detailed_x = np.arange(x1, x2, 0.02)
        detailed_wbgt = f(detailed_x)

        full_detailed_x = np.append(full_detailed_x, detailed_x)

        for i, v in enumerate(wbgt_status.values()):
            modified_wbgt = np.where(detailed_wbgt > v.max, v.max, detailed_wbgt)
            levels[i] = np.append(levels[i], modified_wbgt)

    for i, v in enumerate(wbgt_status.values()):
        plt.fill_between(
            x=full_detailed_x,
            y1=v.min,
            y2=levels[i],
            where=levels[i] >= v.min,
            color=v.color,
            alpha=alpha,
        )

    plt.plot(virtual_x, wbgt_list, color="black", marker="o", lw=3)

    plt.grid()

    plt.ylabel("W\nG\nB\nT\n[C°]", va="center", rotation=0, size=15, labelpad=20)
    plt.tight_layout()  # レイアウト

    if os.environ.get("tsfm_debug"):  # デバッグ用設定
        plt.show()

    else:  # 本番環境用設定
        plt.xticks(
            [i for i in range(len(time_list))],
            [f"{time.split('/')[2].split(':')[0]}時" for time in time_list],
            font=pathlib.Path(__file__).parent / "font.ttf",
        )
        graph = output_graph()  # グラフプロット

    return graph


def location2wbgt(ido: float, keido: float, hours: int = 24) -> tuple[list[float], list[str]]:
    """wbgt温度の計算
    緯度・経度を用いて，Open-Meteo API(open-meteo.com)から，
        - 温度
        - 湿度
        - 直達日射量
        - 散乱日射量
        - 風速
        を取得します
        これらの値からwbgt温度を計算します
        (https://blog.obniz.com/news/obniz-wbgt-service.html)
    Args:
        - ido (float): 緯度
        - keido (float): 経度
    Returns:
        - wbgts_list list[float]: wbgt温度（24時間分）
        - time_list list[str]: １時間ごとの時間（24時間分）
    """

    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={ido}&longitude={keido}"
        "&hourly=temperature_2m,relativehumidity_2m,direct_radiation,diffuse_radiation,"
        "windspeed_10m&current_weather=true&timezone=Asia%2FTokyo"
    )

    wbgts_list: list[float] = []
    time_list: list[str] = []

    year: int = datetime.now(timezone(timedelta(hours=9), "JST")).year

    with request.urlopen(url) as r:
        body = json.loads(r.read())

        tdate = body["current_weather"]["time"]
        index_now_time = body["hourly"]["time"].index(tdate)

        for index in range(index_now_time, index_now_time + hours):
            time = body["hourly"]["time"][index]

            time = time.replace(f"{year}-", "")
            time = time.replace("-", "/")
            time = time.replace("T", "/")

            time_list.append(time)

            temperature = body["hourly"]["temperature_2m"][index]
            humidity = body["hourly"]["relativehumidity_2m"][index]
            direct_radiation = body["hourly"]["direct_radiation"][index] / 1000
            diffuse_radiation = body["hourly"]["diffuse_radiation"][index] / 1000
            windspeed_10m = abs(body["hourly"]["windspeed_10m"][index] * 1000 / 3600)

            wbgt = (
                0.735 * temperature
                + 0.0374 * humidity
                + 0.00292 * temperature * humidity
                + 7.619 * (direct_radiation + diffuse_radiation)
                - 4.557 * (direct_radiation + diffuse_radiation) ** 2
                - 0.0572 * windspeed_10m
                - 4.064
            )
            wbgts_list.append(round(wbgt, 3))

    # 現在から24時間後の暑さ指数の予測値と時刻が入った配列
    return wbgts_list, time_list


def wbgt_indicator(WBGT: float) -> str:
    """wbgt温度による熱中症リスクの診断
    Args:
        WBGT (float): wbgt温度
    Returns:
        message (str): 危険度合のメッセージ
    """

    for v in wbgt_status.values():
        if v.min <= WBGT < v.max:
            return v.message
    else:
        return "None"


if __name__ == "__main__":
    os.environ["tsfm_debug"] = "1"
    x = [i for i in range(0, 24)]
    y = [random.randint(20, 38) for _ in x]
    plot_graph(x, y)
