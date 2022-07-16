from django.urls import path
from app import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('Map/', views.MapView.as_view(), name='Map'),
    path('Mapdetail/', views.MapView.basyodetail, name='Mapdetail'),
    path('basyomap/', views.MapView.basyomap, name='basyomap'),
    ]