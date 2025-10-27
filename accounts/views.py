# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def custom_logout(request):
    logout(request)
    return redirect('home')

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from brokers.models import Broker

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Le user_type est maintenant sauvegardé via le formulaire
            user.save()
            
            # Si l'utilisateur s'inscrit en tant que courtier, créer son profil courtier
            if user.user_type == 'broker':
                Broker.objects.create(
                    user=user,
                    is_approved=False,  # Doit être approuvé par l'admin
                    description=f"Courtier inscrit le {user.date_joined.strftime('%d/%m/%Y')}"
                )
            
            login(request, user)
            
            # Redirection basée sur le type d'utilisateur
            if user.user_type == 'broker':
                messages.success(request, "🎉 Bienvenue courtier ! Votre compte est en attente de validation.")
                return redirect('broker_dashboard')
            else:
                messages.success(request, "🎉 Bienvenue sur Carbura ! Commencez à explorer les stations près de chez vous.")
                return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    """Page de profil utilisateur"""
    context = {}
    if request.user.user_type == 'broker':
        try:
            context['broker_profile'] = request.user.broker_profile
        except Broker.DoesNotExist:
            # Créer le profil courtier s'il n'existe pas
            context['broker_profile'] = Broker.objects.create(user=request.user)
    
    return render(request, 'accounts/profile.html', context)