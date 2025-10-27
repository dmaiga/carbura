# brokers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from brokers.models import Broker
from stations.models import StationReport,Station
from missions.models import Mission, MissionApplication
from django.utils import timezone
from datetime import timedelta

# missions/views.py

@login_required
def accept_mission(request, mission_id):
    """Accepter une mission (pour le citoyen)"""
    mission = get_object_or_404(Mission, id=mission_id, citizen=request.user)
    
    if request.method == 'POST':
        broker_id = request.POST.get('broker_id')
        application = get_object_or_404(MissionApplication, mission=mission, broker_id=broker_id)
        
        # Accepter la mission
        mission.broker_id = broker_id
        mission.status = 'accepted'
        mission.accepted_at = timezone.now()
        mission.price = application.proposed_price
        mission.save()
        
        # Marquer le courtier comme non disponible
        broker_profile = Broker.objects.get(user_id=broker_id)
        broker_profile.is_available = False
        broker_profile.save()
        
        # Supprimer les autres candidatures
        mission.applications.exclude(broker_id=broker_id).delete()
        
        messages.success(request, f"Mission acceptée ! Courtier: {mission.broker.username}")
        return redirect('mission_detail', mission_id=mission.id)
    
    return redirect('mission_detail', mission_id=mission.id)


@login_required
def create_mission(request, station_id):
    """Créer une mission pour une station"""
    station = get_object_or_404(Station, id=station_id)
    
    if request.method == 'POST':
        mission = Mission.objects.create(
            citizen=request.user,
            station=station,
            fuel_type=request.POST.get('fuel_type', 'essence'),
            quantity=request.POST.get('quantity', 10),
            special_instructions=request.POST.get('special_instructions', '')
        )
        
        messages.success(request, "Mission créée ! Les courtiers peuvent maintenant postuler.")
        return redirect('mission_detail', mission_id=mission.id)
    
    return render(request, 'missions/create_mission.html', {'station': station})

# missions/views.py
@login_required
def mission_detail(request, mission_id):
    """Détail d'une mission"""
    mission = get_object_or_404(Mission, id=mission_id)
    
    # Vérifier les permissions
    if mission.citizen != request.user and mission.broker != request.user and not request.user.is_staff:
        messages.error(request, "Accès non autorisé à cette mission.")
        return redirect('home')
    
    applications = mission.applications.all() if mission.status == 'pending' else None
    
    context = {
        'mission': mission,
        'applications': applications,
    }
    return render(request, 'missions/mission_detail.html', context)
@login_required
def update_mission_status(request, mission_id, status):
    """Mettre à jour le statut d'une mission"""
    mission = get_object_or_404(Mission, id=mission_id)
    
    # Vérifier les permissions
    if mission.broker != request.user and mission.citizen != request.user:
        messages.error(request, "Action non autorisée.")
        return redirect('home')
    
    valid_statuses = ['in_progress', 'completed', 'cancelled']
    if status in valid_statuses:
        mission.status = status
        
        if status == 'completed':
            mission.completed_at = timezone.now()
            # Rendre le courtier disponible à nouveau
            if mission.broker:
                broker_profile = Broker.objects.get(user=mission.broker)
                broker_profile.is_available = True
                broker_profile.completed_missions += 1
                broker_profile.save()
        
        mission.save()
        messages.success(request, f"Statut mis à jour: {mission.get_status_display()}")
    
    return redirect('mission_detail', mission_id=mission.id)
from django.http import JsonResponse

@login_required
def rate_mission(request, mission_id):
    """Noter une mission terminée (version AJAX)"""
    mission = get_object_or_404(Mission, id=mission_id, citizen=request.user, status='completed')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        review = request.POST.get('review', '')
        
        mission.rating = rating
        mission.review = review
        mission.save()
        
        # Mettre à jour la note du courtier
        if mission.broker and mission.broker.broker_profile:
            broker = mission.broker.broker_profile
            all_ratings = Mission.objects.filter(
                broker=mission.broker, 
                rating__isnull=False
            ).values_list('rating', flat=True)
            
            if all_ratings:
                broker.rating = sum(all_ratings) / len(all_ratings)
                broker.save()
        
        return JsonResponse({'success': True, 'message': 'Merci pour votre évaluation !'})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@login_required
def citizen_dashboard(request):
    """Tableau de bord citoyen - Voir toutes ses missions"""
    if request.user.user_type != 'citizen':
        messages.info(request, "Cette page est réservée aux citoyens.")
        return redirect('home')
    
    # Récupérer toutes les missions du citoyen
    missions = Mission.objects.filter(citizen=request.user).order_by('-created_at')
    
    # Statistiques
    total_missions = missions.count()
    completed_missions = missions.filter(status='completed').count()
    pending_missions = missions.filter(status__in=['pending', 'accepted', 'in_progress']).count()
    
    context = {
        'missions': missions,
        'total_missions': total_missions,
        'completed_missions': completed_missions,
        'pending_missions': pending_missions,
    }
    return render(request, 'missions/citizen_dashboard.html', context)