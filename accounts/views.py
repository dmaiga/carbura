# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm,CustomAuthenticationForm
from brokers.models import Broker
from django.db.models import Q

def custom_logout(request):
    logout(request)
    return redirect('home')


def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenue {user.username} !")
                
                # Redirection selon le type d'utilisateur
                if user.user_type == 'broker':
                    return redirect('broker_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Identifiants invalides.")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

from django.contrib.auth import login, authenticate

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Si l'utilisateur s'inscrit en tant que courtier, créer son profil courtier
            if user.user_type == 'broker':
                Broker.objects.create(
                    user=user,
                    is_approved=False,
                    description=f"Courtier inscrit le {user.date_joined.strftime('%d/%m/%Y')}"
                )
            
            # Authentifier l'utilisateur avec ses identifiants
            user = authenticate(
                request,
                username=user.username,  # ou user.email, user.phone
                password=form.cleaned_data.get('password1')
            )
            
            if user is not None:
                login(request, user)
                
                # Redirection basée sur le type d'utilisateur
                if user.user_type == 'broker':
                    messages.success(request, "🎉 Bienvenue courtier ! Votre compte est en attente de validation.")
                    return redirect('broker_dashboard')
                else:
                    messages.success(request, "🎉 Bienvenue sur Carbura ! Commencez à explorer les stations près de chez vous.")
                    return redirect('home')
            else:
                messages.error(request, "Erreur lors de la connexion automatique. Veuillez vous connecter manuellement.")
                return redirect('login')
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