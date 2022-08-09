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
            return render(
                request=request,
                template_name="app/user.html",
                context={"lat": ido, "lon": keido, "id": request.GET.get("id")},
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
            context["next_page"] = f"{self.request._current_scheme_host}/user/"  # type: ignore

        else:
            context["button_message"] = "この場所の情報を見る"
            context["next_page"] = f"{self.request._current_scheme_host}/Mapdetail/"  # type: ignore

        return context

    # def get (self, request: HttpRequest) -> None:
    #     print(request.GET.get("type", default=None))


class User(TemplateView):
    template_name: str = "app/user.html"

    def do_save(self, id: int, ido: float, keido: float):
        print(id, ido, keido)

    def post(self, request: HttpRequest) -> Any:
        query: dict[str, list[Any]] = urllib.parse.parse_qs(request.META.get("HTTP_REFERER"))  # type:ignore
        print(request.POST.items())
        self.do_save(id=int(query.get("id")[0]), ido=request.POST.get("ido"), keido=request.POST.get("keido"))  # type: ignore

        ret = render(
            request=request,
            template_name="app/user.html",
            context={
                "user": request.user,
                # これらの値は，DBから取得する
                "location_1": "test1",
                "ido_1": 40,
                "keido_1": 135,
                "location_2": "test2",
                "ido_2": 40,
                "keido_2": 135,
                "location_3": "test3",
                "ido_3": 140,
                "keido_3": 135,
            },
        )

        #     print(ret)

        return ret

    def get_context_data(self, **kwargs):  # type:ignore
        print(self.request)
        context = super().get_context_data(**kwargs)
        # context[""] =
        context["link_1"] = f"{self.request._current_scheme_host}/Map/?type=location&id=1"  # type: ignore
        context["link_2"] = f"{self.request._current_scheme_host}/Map/?type=location&id=2"  # type: ignore
        context["link_3"] = f"{self.request._current_scheme_host}/Map/?type=location&id=3"  # type: ignore

        return context

    # def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    #     context = super().get(request, *args, **kwargs)
    #     return context


class SetLocationName(TemplateView):
    template_name: str = "app/userlocation.html"

    def do_save(self, id: int, ido: float, keido: float):
        print(id, ido, keido)

    def post(self, request: HttpRequest) -> Any:
        query: dict[str, list[Any]] = urllib.parse.parse_qs(request.META.get("HTTP_REFERER"))  # type:ignore
        print(request.POST.items())
        self.do_save(id=int(query.get("id")[0]), ido=request.POST.get("ido"), keido=request.POST.get("keido"))  # type: ignore

        ret = render(
            request=request,
            template_name="app/user.html",
            context={
                "user": request.user,
                # これらの値は，DBから取得する
                "location_1": "test1",
                "ido_1": 40,
                "keido_1": 135,
                "location_2": "test2",
                "ido_2": 40,
                "keido_2": 135,
                "location_3": "test3",
                "ido_3": 140,
                "keido_3": 135,
            },
        )

        #     print(ret)

        return ret

    def get_context_data(self, **kwargs):  # type:ignore
        print(self.request)
        context = super().get_context_data(**kwargs)
        # context[""] =
        context["link_1"] = f"{self.request._current_scheme_host}/Map/?type=location&id=1"  # type: ignore
        context["link_2"] = f"{self.request._current_scheme_host}/Map/?type=location&id=2"  # type: ignore
        context["link_3"] = f"{self.request._current_scheme_host}/Map/?type=location&id=3"  # type: ignore

        return context

    # def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
    #     context = super().get(request, *args, **kwargs)
    #     return context
