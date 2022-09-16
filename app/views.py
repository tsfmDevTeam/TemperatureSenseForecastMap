import json
import os
import urllib
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Union, cast

import requests
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render  # type:ignore
from django.urls import reverse  # type:ignore
from django.views.generic import TemplateView

from . import db2geojson, geo_apis, wbgt_util
from .forms import LoginForm, SignupForm
from .location_search import near_observatory
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

            return render(
                request=request,
                template_name="app/locationname.html",
                context={"ido": ido, "keido": keido},
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


class MapDetail(TemplateView):
    template_name = "app/detail.html"

    def post(self, request: HttpRequest):
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

        for v in wbgt_util.wbgt_status.values():
            if v.min <= wbgt_now < v.max:
                wbgt_severity_now = v.level
                break
        else:
            wbgt_severity_now = 0

        wbgt_max = max(wbgt_list)
        wbgt_status_max = wbgt_util.wbgt_indicator(WBGT=wbgt_max)
        max_time = time_list[wbgt_list.index(wbgt_max)]

        wbgt_and_status: list[dict[str, Union[str, float]]] = []

        for wbgt, time in zip(wbgt_list, time_list):
            status = wbgt_util.wbgt_indicator(WBGT=wbgt)

            wbgt_and_status.append({"wbgt": wbgt, "status": status, "time": time[6:]})

        # 周辺地域の取得
        tikaku = geo_apis.find_near(ido=ido, keido=keido)

        juusyo = tikaku[0]["juusyo"]

        tweet_message = (
            f"{juusyo}の暑さ指数は{wbgt_severity_now}です！\n危険度は、{wbgt_status_now}\n熱中症にお気をつけてよい一日をお過ごしください！\n#技育展_tsfm #暑さ指数"
        )
        hashed_message = urllib.parse.quote(tweet_message)
        contribution_tweets_URL = "https://twitter.com/intent/tweet?text=" + hashed_message

        return render(
            request=request,
            template_name="app/detail.html",
            context={
                "juusyo": juusyo,
                "lat": ido,
                "lon": keido,
                "wbgt_now": wbgt_now,
                "wbgt_max": wbgt_max,
                "wbgt_status_now": wbgt_status_now,
                "wbgt_status_max": wbgt_status_max,
                "wbgt_and_status": wbgt_and_status,
                "max_time": max_time,
                "chart": chart,
                "contribution_tweets_URL": contribution_tweets_URL,
            },
        )


class UserPage(TemplateView):
    template_name: str = "app/user.html"

    def get_location_from_db(self, uid: int) -> list[Any]:
        locations: list[Any] = []
        for query in location.objects.filter(user_id=uid):
            name = query.location_name
            location_id = query.location_id

            try:
                POINT = point_name.objects.get(id=location_id)
                ido = POINT.ido
                keido = POINT.keido
            except ObjectDoesNotExist:
                ido = 0
                keido = 0
            locations.append({"ido": ido, "keido": keido, "name": name})
        return locations

    def _do_save(self, name: str, ido: float, keido: float, uid: int):
        near_point_obj = near_observatory(float(ido), float(keido))
        near_locationID = near_point_obj.id  # type:ignore
        kansokujo_name = near_point_obj.name  # type:ignore

        location.objects.update_or_create(
            location_name=name,
            location_id=near_locationID,
            kansokujo_name=kansokujo_name,
            user_id_id=uid,
        )

    def _generate_common_context(self) -> dict[str, Any]:
        context: dict[str, Any] = {}

        context["user_name"] = self.request.user.username  # type: ignore
        context["user_email"] = self.request.user.email  # type: ignore
        context["user_id"] = self.request.user.id  # type: ignore

        context["locations"] = json.dumps(self.get_location_from_db(uid=self.request.user.id))  # type: ignore
        context["link"] = f"{self.request._current_scheme_host}/Map/?type=location"  # type: ignore
        context["detail"] = f"{self.request._current_scheme_host}/Mapdetail/"  # type: ignore

        return context

    def post(self, request: HttpRequest):
        print(request.POST)

        context = self._generate_common_context()

        if "delete" in request.POST.keys():
            # 地点削除

            loc_name = request.POST.get("delete", "0")
            print(loc_name)
            # ユーザー存在判定

            try:
                target = location.objects.get(location_name=loc_name)
                print(target)
                print(str(target.user_id) == str(request.user.username))  # type: ignore
                if str(target.user_id) == str(request.user.username):  # type: ignore
                    target.delete()
            except ObjectDoesNotExist:
                pass

        elif "addname" not in request.POST.keys() and "keido" in request.POST.keys():
            print("ido & keido")
            # 地点追加コマンド
            context["ido"] = request.POST.get("ido")
            context["keido"] = request.POST.get("keido")
            context["submit_link"] = f"{self.request._current_scheme_host}/user/"  # type:ignore
            context["type"] = "addloc"
            # loc_id = int(request.POST.get("add", "0"))
        elif "addname" in request.POST.keys():
            self._do_save(
                name=request.POST.get("addname"),  # type:ignore
                ido=request.POST.get("ido"),  # type:ignore
                keido=request.POST.get("keido"),  # type:ignore
                uid=request.user.id,  # type:ignore
            )

        else:
            print("other")

        return render(request=request, template_name="app/user.html", context=context)  # type: ignore

    def get_context_data(self):  # type:ignore
        return self._generate_common_context()


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
        now_day: int = datetime.now(timezone(timedelta(hours=9), "JST")).day

        param = {
            "MAPBOX_TOKEN": os.getenv("MAPBOX_TOKEN"),
            "now_day": now_day,
            "now_hour": now_hour,
            "time_label": f"{now_day}日 {now_hour}時",
        }

        return render(request, "app/HeatMap.html", param)


class HeatMap_framesaki_view(TemplateView):
    template_name = "app/HeatmapFrame.html"


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
