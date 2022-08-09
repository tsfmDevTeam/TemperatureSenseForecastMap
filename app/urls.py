from django.urls import path

from app import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("BuffView/", views.BuffView.as_view(), name="BuffView"),
    path("WF/", views.WFView.as_view(), name="WF"),
    path("Map/", views.MapView.as_view(), name="Map"),
    path("Mapdetail/", views.MapView.as_view(), name="Mapdetail"),
    path("user/", views.User.as_view(), name="user"),
    path("locationname/", views.SetLocationName.as_view(), name="userloc"),
]
