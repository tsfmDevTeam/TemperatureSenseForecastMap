from typing import Any, Union

from django.shortcuts import render
from django.views.generic import TemplateView

from src import geo_apis, wgbt


class BuffView(TemplateView):
    template_name = "app/buff.html"


class IndexView(TemplateView):
    template_name = "app/index.html"


class WFView(TemplateView):
    template_name = "app/WF.html"


class MapView(TemplateView):
    template_name = "app/Map.html"
    # next_page =

    def basyodetail(request):
        lat: float = request.POST.get("lat")
        lon: float = request.POST.get("lng")

        wgbt_list, time_list, chart = wgbt.location2wgbt(ido=lat, keido=lon)

        wgbt_now = wgbt_list[0]
        wgbt_status_now = wgbt.wgbt_indicator(WBGT=wgbt_now)

        wgbt_max = max(wgbt_list)
        wgbt_status_max = wgbt.wgbt_indicator(WBGT=wgbt_max)
        max_time = time_list[wgbt_list.index(wgbt_max)]

        wgbt_and_status: list[dict[str, Union[str, float]]] = []

        for WGBT, time in zip(wgbt_list, time_list):
            status = wgbt.wgbt_indicator(WBGT=WGBT)

            wgbt_and_status.append({"WGBT": WGBT, "status": status, "time": time[6:]})

        # 周辺地域の取得
        tikaku = geo_apis.find_near(ido=lat, keido=lon)

        return render(
            request=request,
            template_name="app/detail.html",
            context={
                "lat": lat,
                "lon": lon,
                "wgbt_now": wgbt_now,
                "wgbt_max": wgbt_max,
                "wgbt_status_now": wgbt_status_now,
                "wgbt_status_max": wgbt_status_max,
                "wgbt_and_status": wgbt_and_status,
                "tikaku": tikaku,
                "max_time": max_time,
                "chart": chart,
            },
        )


class MapSelection(MapView):
    pass


class User(TemplateView):
    template_name: str = "app/user.html"

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        print(request)
        if request.method == "POST":
            if "save_button" in request.POST:
                print(f"{request.POST}")
                # print(f"{request.location_1}, {request.location_2}, {request.location_3}")

        return render(
            request=request,
            template_name="app/user.html",
            context={
                "user": request.user,
                "location1": "test1",
                "location2": "test2",
                "location3": "test3",
            },
        )

    def get_context_data(self, **kwargs):  # type:ignore
        context = super().get_context_data(**kwargs)
        # context[""] =

        return context
