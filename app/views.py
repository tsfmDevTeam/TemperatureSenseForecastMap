from random import randint
import urllib
from typing import Any, Dict, Union

from django.http import HttpRequest
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

    def post(self, request: HttpRequest):

        ido: float = request.POST.get("ido")  # type: ignore
        keido: float = request.POST.get("keido")  # type: ignore

        if request.GET.get("type") == "location":
            print(f"mapview ,{ido} {keido}")
            return render(
                request=request,
                template_name="app/locationname.html",
                context={"ido": ido, "keido": keido},
            )

        else:
            wgbt_list, time_list, chart = wgbt.location2wgbt(ido=ido, keido=keido)

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
            tikaku = geo_apis.find_near(ido=ido, keido=keido)

            return render(
                request=request,
                template_name="app/detail.html",
                context={
                    "lat": ido,
                    "lon": keido,
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

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.GET.get("type") == "location":
            context["button_message"] = "この場所を選択する"
            context["next_page"] = f"{self.request._current_scheme_host}/locationname/"  # type: ignore

        else:
            context["button_message"] = "この場所の情報を見る"
            context["next_page"] = f"{self.request._current_scheme_host}/Mapdetail/"  # type: ignore

        return context


class User(TemplateView):
    template_name: str = "app/user.html"

    def get_location_from_db(self) -> list[str]:
        return [str(i) for i in range(randint(0, 3))]

    def get_context_data(self, **kwargs):  # type:ignore
        print(self.request)
        context = super().get_context_data(**kwargs)
        # context[""] =
        context["location_1"] = "test"

        context["link"] = f"{self.request._current_scheme_host}/Map/?type=location"  # type: ignore

        return context


class SetLocationName(TemplateView):
    template_name: str = "app/locationname.html"

    def do_save(self, name: str, ido: float, keido: float):
        print(name, ido, keido)

    def post(self, request: HttpRequest) -> Any:
        if "save" in request.POST:
            self.do_save(
                name=request.POST.get("location_name"),  # type: ignore
                ido=request.POST.get("ido"),  # type: ignore
                keido=request.POST.get("keido"),  # type: ignore
            )

            ret = render(request=request, template_name="app/user.html", context={})
            return ret
        else:
            print("POStview", request.POST.items())

            ret = render(
                request=request,
                template_name="app/locationname.html",
                context={
                    "location_id": request.POST.get("location_id"),
                    "ido": request.POST.get("ido"),
                    "keido": request.POST.get("keido"),
                },
            )
            return ret

    def get_context_data(self, **kwargs):  # type:ignore
        print("locatename META", self.request.META)
        context = super().get_context_data(**kwargs)

        return context
