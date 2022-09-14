from datetime import datetime, timedelta, timezone
import json
import os
import urllib
from typing import Any, Dict, Union, cast

import requests
from django.contrib.auth import login, logout
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render  # type:ignore
from django.urls import reverse
from django.views.generic import TemplateView

from .location_search import near_observatory
from . import geo_apis, wbgt_util, db2geojson

from .forms import LoginForm, SignupForm
from .models import location, point_name


class IndexView(TemplateView):
    template_name = "app/index.html"


class AboutView(TemplateView):
    template_name = "app/about.html"


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

                makeUrl: str = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
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

                wbgt_and_status.append({"wbgt": wbgt, "status": status, "time": time[6:]})

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
            location_id = query.location_id
            POINT = point_name.objects.filter(id=int(location_id))
            for locate in POINT:
                ido = locate.ido
                keido = locate.keido
            print(ido, keido)
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

        near_point_obj = near_observatory(float(ido), float(keido))
        # near_ido = near_point_obj.ido
        # near_keido = near_point_obj.keido
        near_locationID = near_point_obj.id
        kansokujo_name = near_point_obj.name

        location.objects.update_or_create(
            # location_name=name, ido=near_ido, keido=near_keido, user_id_id=uid
            location_name=name,
            location_id=near_locationID,
            kansokujo_name=kansokujo_name,
            user_id_id=uid,
        )

        print(name, ido, keido)
        print(near_point_obj.name, kansokujo_name, near_locationID)

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


class Signup(TemplateView):
    template_name: str = "app/user_admin/signup.html"

    def post(self, request: HttpRequest):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            # サインアップ成功時にsuccess_signup.htmlに遷移
            return HttpResponseRedirect(reverse("success_signup"))

        param = {"form": form}
        return render(request, "app/user.html", param)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        form = SignupForm()
        param = {"form": form}
        return render(request, "app/user_admin/signup.html", param)


class Login(TemplateView):
    template_name: str = "app/user_admin/login.html"

    def post(self, request: HttpRequest):
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

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        form = LoginForm()
        next = request.GET.get("next")
        param = {"form": form, "next": next}

        return render(request, "app/user_admin/login.html", param)


class Logout(TemplateView):
    template_name: str = "app/user_admin/logout.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        logout(self.request)
        return render(self.request, "app/user_admin/logout.html")


class HeatMap_view(TemplateView):
    template_name = "app/Heatmap.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):

        db2geojson.data2geojson()

        now_hour: int = datetime.now(timezone(timedelta(hours=9), "JST")).hour

        param = {
            "MAPBOX_TOKEN": os.getenv("MAPBOX_TOKEN"),
            "now_hour": now_hour,
            "time_label": f"{now_hour}時",
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
