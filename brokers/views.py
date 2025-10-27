# brokers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Broker
from django.utils import timezone
from datetime import timedelta
from missions.models import Mission, MissionApplication
from django.contrib import messages

@login_required
def become_broker(request):
    """Devenir courtier"""
    if request.method == 'POST':
        # Créer le profil courtier
        broker, created = Broker.objects.get_or_create(
            user=request.user,
            defaults={
                'description': request.POST.get('description', ''),
                'is_approved': False  # En attente de validation admin
            }
        )
        
        # Mettre à jour le type d'utilisateur
        request.user.user_type = 'broker'
        request.user.save()
        
        messages.success(request, "Votre demande de courtier a été soumise ! En attente de validation.")
        return redirect('broker_dashboard')
    
    return render(request, 'brokers/become_broker.html')

# brokers/views.py
@login_required
def broker_dashboard(request):
    """Tableau de bord courtier"""
    if request.user.user_type != 'broker':
        messages.info(request, "Vous devez être courtier pour accéder à cette page.")
        return redirect('home')
    
    try:
        broker_profile = Broker.objects.get(user=request.user)
    except Broker.DoesNotExist:
        # Créer le profil courtier s'il n'existe pas
        broker_profile = Broker.objects.create(user=request.user, is_approved=False)
        messages.info(request, "Votre profil courtier a été créé. En attente de validation.")
    
    # Missions du courtier
    my_missions = Mission.objects.filter(broker=request.user).order_by('-created_at')
    
    # Missions disponibles (seulement si le courtier est approuvé)
    available_missions = Mission.objects.filter(status='pending').exclude(
        applications__broker=request.user
    ).order_by('-created_at') if broker_profile.is_approved else Mission.objects.none()
    
    context = {
        'broker_profile': broker_profile,
        'my_missions': my_missions,
        'available_missions': available_missions,
    }
    return render(request, 'brokers/dashboard.html', context)


@login_required
def apply_mission(request, mission_id):
    """Postuler à une mission"""
    if request.user.user_type != 'broker':
        return JsonResponse({'error': 'Accès réservé aux courtiers'}, status=403)
    
    mission = get_object_or_404(Mission, id=mission_id, status='pending')
    
    # Vérifier si déjà postulé
    if MissionApplication.objects.filter(mission=mission, broker=request.user).exists():
        messages.warning(request, "Vous avez déjà postulé à cette mission.")
        return redirect('broker_dashboard')
    
    if request.method == 'POST':
        application = MissionApplication.objects.create(
            mission=mission,
            broker=request.user,
            message=request.POST.get('message', ''),
            proposed_price=request.POST.get('proposed_price')
        )
        
        messages.success(request, "Votre candidature a été envoyée !")
        return redirect('broker_dashboard')
    
    return render(request, 'brokers/apply_mission.html', {'mission': mission})
