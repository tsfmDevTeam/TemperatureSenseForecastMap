from django.urls import path

from app import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("Mapsitei/", views.MapView2.juusyo, name="Mapsitei"),
    path("BuffView/", views.BuffView.as_view(), name="BuffView"),
    path('WF/', views.WFView.as_view(), name='WF'),
    path("Map/", views.MapView.as_view(), name="Map"),
    path("Mapdetail/", views.MapView2.basyodetail, name="Mapdetail"),
    path("nameMapdetail/", views.MapView3.basyodetail, name="nameMapdetail"),
    path("Jikkenn/", views.JikkennView.as_view(), name="Jikkenn"),
    path("juusyo/", views.Juusyo.jikkenn, name="juusyo"),
    path("juusyo2/", views.Juusyo.as_view(), name="juusyo2"),

]
