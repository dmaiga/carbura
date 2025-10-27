# missions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:station_id>/', views.create_mission, name='create_mission'),
    path('<int:mission_id>/', views.mission_detail, name='mission_detail'),
    path('<int:mission_id>/accept/', views.accept_mission, name='accept_mission'),
    path('<int:mission_id>/status/<str:status>/', views.update_mission_status, name='update_mission_status'),
    path('<int:mission_id>/rate/', views.rate_mission, name='rate_mission'),
    path('citizen/dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
]