import json
import os
import urllib
from typing import Any, Dict, Union, cast

import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render  # type:ignore
from django.urls import reverse
from django.views.generic import TemplateView

from src import geo_apis, wbgt_util

from .forms import LoginForm, SignupForm
from .models import CustomUser, location, point_name


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

    def post(self, request: HttpRequest):
        if request.GET.get("type") == "location":  # ユーザーページの地点選択モード
            ido: float = request.POST.get("ido")  # type: ignore
            keido: float = request.POST.get("keido")  # type: ignore

            print(f"mapview ,{ido} {keido}")
            return render(
                request=request,
                template_name="app/locationname.html",
                context={"ido": ido, "keido": keido},
            )

        else:  # 暑さ指数の地点選択モード
            ido: Union[float, None] = request.POST.get("ido", None)  # type:ignore
            keido: Union[float, None] = request.POST.get("keido", None)  # type:ignore
            if ido is not None and keido is not None:  # Map からの遷移
                pass

            else:
                ken: Union[str, None] = request.POST.get("geoapi-prefectures")
                siku: Union[str, None] = request.POST.get("geoapi-cities")
                tyouiki: Union[str, None] = request.POST.get("geoapi-towns")

                Address = f"{ken}{siku}{tyouiki}"

                makeUrl: str = (
                    "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
                )
                s_quote: str = urllib.parse.quote(Address)  # type:ignore

                response = requests.get(makeUrl + s_quote)

                ido = cast(float, response.json()[0]["geometry"]["coordinates"][1])
                keido = cast(float, response.json()[0]["geometry"]["coordinates"][0])

            wbgt_list, time_list = wbgt_util.location2wbgt(ido=ido, keido=keido)
            chart = wbgt_util.plot_graph(time_list, wbgt_list)

            wbgt_now = wbgt_list[0]
            wbgt_status_now = wbgt_util.wbgt_indicator(WBGT=wbgt_now)

            wbgt_max = max(wbgt_list)
            wbgt_status_max = wbgt_util.wbgt_indicator(WBGT=wbgt_max)
            max_time = time_list[wbgt_list.index(wbgt_max)]

            wbgt_and_status: list[dict[str, Union[str, float]]] = []

            for wbgt, time in zip(wbgt_list, time_list):
                status = wbgt_util.wbgt_indicator(WBGT=wbgt)

                wbgt_and_status.append(
                    {"wbgt": wbgt, "status": status, "time": time[6:]}
                )

            # 周辺地域の取得
            tikaku = geo_apis.find_near(ido=ido, keido=keido)

            return render(
                request=request,
                template_name="app/detail.html",
                context={
                    "lat": ido,
                    "lon": keido,
                    "wbgt_now": wbgt_now,
                    "wbgt_max": wbgt_max,
                    "wbgt_status_now": wbgt_status_now,
                    "wbgt_status_max": wbgt_status_max,
                    "wbgt_and_status": wbgt_and_status,
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


class UserPage(TemplateView):
    template_name: str = "app/user.html"

    def get_location_from_db(self, uid: int) -> list[Any]:
        locations: list[Any] = []
        for query in location.objects.filter(user_id=uid):
            lid = query.id
            name = query.location_name
            ido = query.ido
            keido = query.keido
            locations.append((lid, name, ido, keido))
        return locations

    def post(self, request: HttpRequest):
        loc_id = int(request.POST.get("text", "0"))

        try:
            if str(location.objects.filter(id=loc_id)[0].user_id) == request.user.username:  # type: ignore
                location.objects.filter(id=loc_id).delete()
        except IndexError:
            pass
        ret = redirect(f"{self.request._current_scheme_host}/user/")  # type: ignore
        return ret

    def get_context_data(self, **kwargs):  # type:ignore
        context = super().get_context_data(**kwargs)

        context["user_name"] = self.request.user.username  # type: ignore
        context["user_email"] = self.request.user.email  # type: ignore
        context["user_id"] = self.request.user.id  # type: ignore

        context["locations"] = json.dumps(self.get_location_from_db(uid=self.request.user.id))  # type: ignore
        context["link"] = f"{self.request._current_scheme_host}/Map/?type=location"  # type: ignore
        return context


class SetLocationName(TemplateView):
    template_name: str = "app/locationname.html"

    def do_save(self, name: str, ido: float, keido: float, uid: int):
        location.objects.update_or_create(
            location_name=name, ido=ido, keido=keido, user_id_id=uid
        )
        print(name, ido, keido)

    def post(self, request: HttpRequest) -> Any:
        if "save" in request.POST:
            self.do_save(
                name=request.POST.get("location_name"),  # type: ignore
                ido=request.POST.get("ido"),  # type: ignore
                keido=request.POST.get("keido"),  # type: ignore
                uid=request.user.id,  # type: ignore
            )

            ret = redirect(f"{self.request._current_scheme_host}/user/")  # type: ignore
            return ret
        else:
            ret = render(
                request=request,
                template_name="app/locationname.html",
                context={
                    "ido": request.POST.get("ido"),
                    "keido": request.POST.get("keido"),
                    "link": f"{self.request._current_scheme_host}/user/",  # type:ignore
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
            # サインアップ成功時にsuccess_signup.htmlに遷移

            return HttpResponseRedirect(reverse("success_signup"))

    else:
        form = SignupForm()

    param = {"form": form}

    return render(request, "app/user_admin/signup.html", param)


# サインアップ成功の表示
def success_signup(request):
    return render(request, "app/user_admin/success_signup.html")


def login_view(request):
    if request.method == "POST":
        next = request.POST.get("next")
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                if next is None:
                    # 既にログインしており、userページにいたならuserページに飛ぶ
                    return redirect(to="/user")
                else:
                    # 既にログインしており、userページ以外にいたならそのページに飛ぶ
                    print(next)
                    return redirect(to=next)
    else:
        form = LoginForm()
        next = request.GET.get("next")

    param = {"form": form, "next": next}

    return render(request, "app/user_admin/login.html", param)


def logout_view(request):
    logout(request)

    return render(request, "app/user_admin/logout.html")


def HeatMap_view(request):
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")

    all_data = []
    for point in point_name.objects.all():
        data = {}
        data["ido"] = point.ido
        data["keido"] = point.keido
        data["wgbt"] = point.wbgt_time_json["wbgt"]
        all_data.append(data)

    # all_data = str(all_data)

    param = {
        "MAPBOX_TOKEN": MAPBOX_TOKEN,
        "all_data": all_data,
    }

    return render(request, "app/HeatMap.html", param)


# @login_required  # 未登録のユーザーのアクセス制限
# def user_view(request):
#     if request.method == "POST":
#         form = LoginForm(request, data=request.POST)
#
#         if form.is_valid():
#             user = form.get_user()
#
#             if user:
#                 login(request, user)
#                 return redirect(to="/app/user_admin/user/")
#
#     else:
#         form = LoginForm()
#         uid = request.user.id
#         locations = []
#
#         for query in location.objects.filter(user_id=uid):
#             lid = query.id
#             name = query.location_name
#             ido = query.ido
#             keido = query.keido
#             locations.append((lid, name, ido, keido))
#
#     param = {
#         "title": "ログイン",
#         "form": form,
#     }
#
#     return render(request, "app/user_admin/user.html", param)


# @login_required
# def other_view(request):
#     users = User.objects.exclude(username=request.user.username)
#
#     params = {
#         'users': users
#     }
#
#     return render(request, 'app/user_admin/other.html', params)
