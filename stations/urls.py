# stations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('report/', views.report_station, name='report_station'),
    path('station/<int:station_id>/', views.station_detail, name='station_detail'),
    path('station/<int:station_id>/confirm/', views.confirm_station, name='confirm_station'),
    path('api/station/<int:station_id>/indicators/', views.station_indicators_api, name='station_indicators_api'),
]