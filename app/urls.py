from django.urls import path

from app import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("locationname/", views.SetLocationName.as_view(), name="userloc"),
    path("Map/", views.MapView.as_view(), name="Map"),
    path("Mapdetail/", views.MapView.as_view(), name="Mapdetail"),
    path("user/", views.UserPage.as_view(), name="user"),
    path("HeatMap/", views.HeatMap_view.as_view(), name="HeatMap"),
    # 以下ログイン関連
    path("signup/", views.Signup.as_view(), name="signup"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
]
