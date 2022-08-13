import json
import urllib
from random import randint
from typing import Any, Dict, Union

import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect, render  # type:ignore
from django.views.generic import TemplateView

from src import geo_apis, wgbt

from .forms import LoginForm, SignupForm


class BuffView(TemplateView):
    template_name = "app/buff.html"


class IndexView(TemplateView):
    template_name = "app/index.html"


class WFView(TemplateView):
    template_name = "app/WF.html"

    def post(self, request: HttpRequest):
        pass


class JikkennView(TemplateView):
    template_name = "app/juuyojikkenn.html"


class MapView(TemplateView):
    template_name = "app/Map.html"

    def juusyomap(request):
        ken = request.POST.get("geoapi-prefectures")
        siku = request.POST.get("geoapi-cities")
        tyouiki = request.POST.get("geoapi-towns")

        juusyo = ken + siku + tyouiki

        print(juusyo)

        Address = juusyo
        makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
        s_quote = urllib.parse.quote(Address)
        response = requests.get(makeUrl + s_quote)

        print("-------------------------------")
        print(response.json()[0]["geometry"]["coordinates"][1])
        print(response.json()[0]["geometry"]["coordinates"][0])
        ido = response.json()[0]["geometry"]["coordinates"][1]
        keido = response.json()[0]["geometry"]["coordinates"][0]

        return render(
            request,
            "app/juusyojikkenn3.html",
            {
                "juusyo": juusyo,
                "ido": ido,
                "keido": keido,
            },
        )

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


class JuusyokennsakuView(TemplateView):
    def basyodetail(request):
        ken = request.POST.get("geoapi-prefectures")
        siku = request.POST.get("geoapi-cities")
        tyouiki = request.POST.get("geoapi-towns")

        juusyo = ken + siku + tyouiki

        print(juusyo)

        Address = juusyo
        makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
        s_quote = urllib.parse.quote(Address)
        response = requests.get(makeUrl + s_quote)

        lat = response.json()[0]["geometry"]["coordinates"][1]
        lon = response.json()[0]["geometry"]["coordinates"][0]

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
            request,
            "app/detail.html",
            {
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


class UserPage(TemplateView):
    template_name: str = "app/user.html"

    def get_location_from_db(self) -> list[str]:
        return [str(randint(100, 200)) for _ in range(randint(1, 3))]

    def get_context_data(self, **kwargs):  # type:ignore
        print(self.request)
        context = super().get_context_data(**kwargs)
        # context[""] =
        context["location_1"] = "test"

        context["locations"] = json.dumps(loc_data)
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
        context = super().get_context_data(**kwargs)

        return context


class Juusyo(TemplateView):
    template_name = "app/juuyojikkenn.html"

    def jikkenn(request):
        ken = request.POST.get("aa")
        print(ken)
        return render(
            request,
            "app/juuyojikkenn2.html",
            {
                "ken": ken,
                "chart": chart,
            },
        )


def signup_view(request):
    if request.method == "POST":

        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()

    else:
        form = SignupForm()

    param = {"form": form}

    return render(request, "app/user_admin/signup.html", param)


def login_view(request):
    if request.method == "POST":
        next = request.POST.get("next")
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                if next == "None":
                    # 既にログインしており、userページにいたならuserページに飛ぶ
                    return redirect(to="/app/user_admin/user.html")
                else:
                    # 既にログインしており、userページ以外にいたならそのページに飛ぶ
                    return redirect(to=next)
    else:
        form = LoginForm()
        next = request.GET.get("next")

    param = {"form": form, "next": next}

    return render(request, "app/user_admin/login.html", param)


def logout_view(request):
    logout(request)

    return render(request, "app/user_admin/logout.html")


@login_required  # 未登録のユーザーのアクセス制限
def user_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                return redirect(to="/app/user_admin/user/")

    else:
        form = LoginForm()

    param = {
        "title": "ログイン",
        "form": form,
    }

    return render(request, "app/user_admin/user.html", param)


# @login_required
# def other_view(request):
#     users = User.objects.exclude(username=request.user.username)
#
#     params = {
#         'users': users
#     }
#
#     return render(request, 'app/user_admin/other.html', params)
