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
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # path("user/", views.user_view, name="user"),
    # path('other/', views.other_view, name='other'),
    path("success_signup/", views.success_signup, name="success_signup"),
]
