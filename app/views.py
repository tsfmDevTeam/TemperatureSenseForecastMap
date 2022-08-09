import urllib
import requests
from typing import Union

from django.shortcuts import render
from django.views.generic import TemplateView

from src import geo_apis, wgbt


class BuffView(TemplateView):
    template_name = "app/buff.html"

class IndexView(TemplateView):
    template_name = "app/index.html"


class WFView(TemplateView):
    template_name = "app/WF.html"


class JikkennView(TemplateView):
    template_name = "app/jikkenn.html"


class MapView(TemplateView):
    template_name = "app/Map.html"

class MapView2(TemplateView):
    def juusyo(request):
        ken = request.POST.get("geoapi-prefectures")
        siku = request.POST.get("geoapi-cities")
        tyouiki = request.POST.get("geoapi-towns")

        juusyo=ken + siku + tyouiki

        print(juusyo)

        Address = juusyo
        makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
        s_quote = urllib.parse.quote(Address)
        response = requests.get(makeUrl + s_quote)

        print('-------------------------------')
        print(response.json()[0]["geometry"]["coordinates"][1])
        print(response.json()[0]["geometry"]["coordinates"][0])
        ido=response.json()[0]["geometry"]["coordinates"][1]
        keido=response.json()[0]["geometry"]["coordinates"][0]

        return render(
            request,
            "app/juusyojikkenn3.html",
            {
                'juusyo': juusyo,
                'ido': ido,
                'keido': keido,
            },
        )

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


class MapView3(TemplateView):

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

class Juusyo(TemplateView):
    template_name = 'app/juuyojikkenn.html'

    def jikkenn(request):
        ken = request.POST.get("aa")
        print(ken)
        return render(
            request,
            "app/juuyojikkenn2.html",
            {
                'ken': ken,
                "chart": chart,
            },
        )


# 以下ログイン関連----------------------------------------------------
from django.shortcuts import redirect
from .forms import SignupForm, LoginForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def signup_view(request):
    if request.method == 'POST':

        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()

    else:
        form = SignupForm()

    param = {
        'form': form
    }

    return render(request, 'app/user_admin/signup.html', param)

def login_view(request):
    if request.method == 'POST':
        next = request.POST.get('next')
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                if next == 'None':
                    # 既にログインしており、userページにいたならuserページに飛ぶ
                    return redirect(to='/app/user_admin/user.html')
                else:
                    # 既にログインしており、userページ以外にいたならそのページに飛ぶ
                    return redirect(to=next)
    else:
        form = LoginForm()
        next = request.GET.get('next')

    param = {
        'form': form,
        'next': next
    }

    return render(request, 'app/user_admin/login.html', param)

def logout_view(request):
    logout(request)

    return render(request, 'app/user_admin/logout.html')

@login_required # 未登録のユーザーのアクセス制限
def user_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            if user:
                login(request, user)
                return redirect(to='/app/user_admin/user/')

    else:
        form = LoginForm()

    param = {
        'title': 'ログイン',
        'form': form,
    }

    return render(request, 'app/user_admin/user.html', param)

# @login_required
# def other_view(request):
#     users = User.objects.exclude(username=request.user.username)
#
#     params = {
#         'users': users
#     }
#
#     return render(request, 'app/user_admin/other.html', params)