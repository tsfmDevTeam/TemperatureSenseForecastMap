from django.contrib.sites import requests
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

import json
import urllib
from urllib import request
import requests
import request


class IndexView(TemplateView):
    template_name = 'app/index.html'


class MapView(TemplateView):
    template_name = 'app/Map.html'

    def basyodetail(request):
        lat = request.POST.get("lat")
        lon = request.POST.get("lng")
        print(lat)

        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            "&hourly=temperature_2m,relativehumidity_2m,direct_radiation,diffuse_radiation,"
            "windspeed_10m&current_weather=true&timezone=Asia%2FTokyo"
        )

        with urllib.request.urlopen(url) as r:
            body = json.loads(r.read())

            tdate = body["current_weather"]["time"]
            index = body["hourly"]["time"].index(tdate)

            temperature = body["hourly"]["temperature_2m"][index]
            humidity = body["hourly"]["relativehumidity_2m"][index]
            direct_radiation = body["hourly"]["direct_radiation"][index]
            diffuse_radiation = body["hourly"]["diffuse_radiation"][index]
            windspeed_10m = body["hourly"]["windspeed_10m"][index]

        wgbt = (
                0.735 * temperature
                + 0.0374 * humidity
                + 0.00292 * temperature * humidity
                + 7.619 * (direct_radiation * diffuse_radiation)
                - 4.557 * (direct_radiation * diffuse_radiation) ** 2
                - 0.0572 * windspeed_10m
                - 4.064
        )

        def wgbt_indicator(WBGT: float) -> str:
            status: list[str] = ["運動は原則中止", "厳重警戒（激しい運動は中止）", "警戒（積極的に休憩", "注意（積極的に水分補給）", "ほぼ安全（適宜水分補給）"]

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

        wgbt_indicator = wgbt_indicator(wgbt)

        # 周辺地域
        url = 'http://geoapi.heartrails.com/api/json?method=searchByGeoLocation&x=' + lon + '&y=' + lat
        result = requests.get(url).json()
        x = 0
        tikaku = []
        try:
            print(result['response']['location'])
        except KeyError:
            return render(request, 'app/basyodetail_error.html')
        for i in result['response']['location']:
            print('〒' + result['response']['location'][x]['postal'], end='')
            print(result['response']['location'][x]['prefecture'], end='')
            print(result['response']['location'][x]['city'], end='')
            print(result['response']['location'][x]['town'], end='')
            print(' 緯度' + result['response']['location'][x]['x'], end='')
            print(' 経度' + result['response']['location'][x]['y'])
            tikaku.append({
                'yuubin': '〒' + result['response']['location'][x]['postal'],
                'juusyo': result['response']['location'][x]['prefecture'] +
                          result['response']['location'][x]['city'] + result['response']['location'][x]['town'],
                'lat': '緯度' + result['response']['location'][x]['x'],
                'lng': '経度' + result['response']['location'][x]['y'],
            }
            )
            x += 1

        return render(request, 'app/detail.html',
                      {"lat": lat, "lon": lon, "wgbt": wgbt, "wgbt_indicator": wgbt_indicator, 'tikaku': tikaku,})


