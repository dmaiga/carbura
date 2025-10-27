# stations/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from .models import Station, StationReport
from .services import check_auto_confirmation
from missions.models import Mission, MissionApplication
from brokers.models import Broker
def home(request):
    """Page d'accueil avec carte/liste des stations"""
    stations = Station.objects.annotate(
        positive_reports=Count('reports', filter=Q(reports__has_fuel=True)),
        total_reports=Count('reports')
    ).order_by('-is_confirmed', '-last_confirmation')
    
    # Stations confirmées (à afficher en priorité)
    confirmed_stations = stations.filter(is_confirmed=True)
    
    # Stations en attente de confirmation
    pending_stations = stations.filter(is_confirmed=False)
    
    context = {
        'confirmed_stations': confirmed_stations,
        'pending_stations': pending_stations,
    }
    return render(request, 'stations/home.html', context)

@login_required
def report_station(request):
    """Formulaire de signalement d'une station"""
    if request.method == 'POST':
        # Créer ou récupérer la station
        station_name = request.POST.get('station_name')
        neighborhood = request.POST.get('neighborhood')
        description = request.POST.get('description', '')
        
        # Rechercher une station existante ou en créer une nouvelle
        station, created = Station.objects.get_or_create(
            name=station_name,
            neighborhood=neighborhood,
            defaults={'description': description}
        )
        
        # Créer le signalement
        report = StationReport.objects.create(
            station=station,
            user=request.user,
            has_fuel=True,  # Pour MVP, on suppose toujours "disponible"
            fuel_type=request.POST.get('fuel_type', 'essence'),
            description=request.POST.get('comment', '')
        )
        
        # Vérifier la confirmation automatique
        check_auto_confirmation(station)
        
        return redirect('station_detail', station_id=station.id)
    
    return render(request, 'stations/report_station.html')

def station_detail(request, station_id):
    """Détail d'une station avec ses signalements et indicateurs de missions"""
    station = get_object_or_404(Station, id=station_id)
    recent_reports = station.reports.all().order_by('-created_at')[:10]
    
    # Vérifier si l'utilisateur a déjà signalé cette station
    user_has_reported = False
    user_missions = []
    user_active_missions = 0
    active_missions_count = 0
    available_brokers_count = 0
    
    if request.user.is_authenticated:
        user_has_reported = station.reports.filter(user=request.user).exists()
        
        # Missions de l'utilisateur pour cette station
        user_missions = Mission.objects.filter(
            citizen=request.user,
            station=station
        ).order_by('-created_at')[:5]  # Dernières 5 missions
        
        user_active_missions = Mission.objects.filter(
            citizen=request.user,
            station=station,
            status__in=['pending', 'accepted', 'in_progress']
        ).count()
    
    # Statistiques générales
    active_missions_count = Mission.objects.filter(
        station=station,
        status__in=['pending', 'accepted', 'in_progress']
    ).count()
    
    # Courtiers disponibles (simplifié)
    available_brokers_count = Broker.objects.filter(
        is_available=True,
        is_approved=True
    ).count()
    
    context = {
        'station': station,
        'recent_reports': recent_reports,
        'user_has_reported': user_has_reported,
        'user_missions': user_missions,
        'user_active_missions': user_active_missions,
        'active_missions_count': active_missions_count,
        'available_brokers_count': available_brokers_count,
    }
    return render(request, 'stations/station_detail.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

@require_GET
def station_indicators_api(request, station_id):
    """API pour les indicateurs dynamiques d'une station"""
    station = get_object_or_404(Station, id=station_id)
    
    # Calculer les indicateurs
    active_missions_count = Mission.objects.filter(
        station=station,
        status__in=['pending', 'accepted', 'in_progress']
    ).count()
    
    available_brokers_count = Broker.objects.filter(
        is_available=True,
        is_approved=True
    ).count()
    
    user_active_missions = 0
    if request.user.is_authenticated:
        user_active_missions = Mission.objects.filter(
            citizen=request.user,
            station=station,
            status__in=['pending', 'accepted', 'in_progress']
        ).count()
    
    return JsonResponse({
        'active_missions_count': active_missions_count,
        'available_brokers_count': available_brokers_count,
        'user_active_missions': user_active_missions,
        'station_id': station_id,
    })

@login_required
def confirm_station(request, station_id):
    """Confirmer un signalement existant"""
    station = get_object_or_404(Station, id=station_id)
    
    # Vérifier que l'utilisateur n'a pas déjà signalé
    if not station.reports.filter(user=request.user).exists():
        StationReport.objects.create(
            station=station,
            user=request.user,
            has_fuel=True,
            description="Je confirme la disponibilité"
        )
        
        # Re-vérifier la confirmation auto
        check_auto_confirmation(station)
    
    return redirect('station_detail', station_id=station.id)