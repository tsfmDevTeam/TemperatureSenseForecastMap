from django.urls import path

from app import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("BuffView/", views.BuffView.as_view(), name="BuffView"),
    path('WF/', views.WFView.as_view(), name='WF'),
    path("Map/", views.MapView.as_view(), name="Map"),
    path("Mapdetail/", views.MapView.basyodetail, name="Mapdetail"),

    # 以下ログイン関連
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/', views.user_view, name='user'),
    # path('other/', views.other_view, name='other'),
]
