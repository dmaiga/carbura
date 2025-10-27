# brokers/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('become-broker/', views.become_broker, name='become_broker'),
    path('dashboard/', views.broker_dashboard, name='broker_dashboard'),
    path('mission/<int:mission_id>/apply/', views.apply_mission, name='apply_mission'),
]
