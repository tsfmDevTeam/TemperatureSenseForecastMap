from django.urls import path

from app import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("BuffView/", views.BuffView.as_view(), name="BuffView"),
    path("Jikkenn/", views.JikkennView.as_view(), name="Jikkenn"),
    path("juusyo/", views.Juusyo.jikkenn, name="juusyo"),
    path("juusyo2/", views.Juusyo.as_view(), name="juusyo2"),
    path("locationname/", views.SetLocationName.as_view(), name="userloc"),
    path("Map/", views.MapView.as_view(), name="Map"),
    path("Mapdetail/", views.MapView.as_view(), name="Mapdetail"),
    path("Mapsitei/", views.MapView.juusyo, name="Mapsitei"),
    path("nameMapdetail/", views.MapView3.basyodetail, name="nameMapdetail"),
    path("user/", views.UserPage.as_view(), name="user"),
    path("WF/", views.WFView.as_view(), name="WF"),
    # 以下ログイン関連
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # path("user/", views.user_view, name="user"),
    # path('other/', views.other_view, name='other'),
]
