from django.shortcuts import render
from django.views.generic import TemplateView

from src import geo_apis, wgbt


class IndexView(TemplateView):
    template_name = "app/index.html"


class MapView(TemplateView):
    template_name = "app/Map.html"

    def basyomap(self):
        kensakumei = request.POST.get("kensakumei")


        return render(
            request,
            "app/detail.html",
            {

                #"lat": lat,
                #"lon": lon,
            },
        )

    def basyodetail(request):
        lat: float = request.POST.get("lat")
        lon: float = request.POST.get("lng")

        wgbt_celsius = wgbt.location2wgbt(ido=lat, keido=lon)
        wgbt_status = wgbt.wgbt_indicator(WBGT=wgbt_celsius)

        # 周辺地域の取得
        tikaku = geo_apis.find_near(ido=lat, keido=lon)

        return render(
            request,
            "app/detail.html",
            {
                "lat": lat,
                "lon": lon,
                "wgbt": wgbt_celsius,
                "wgbt_indicator": wgbt_status,
                "tikaku": tikaku,
            },
        )
