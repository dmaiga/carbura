from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.db.models import Q

class CustomUserCreationForm(UserCreationForm):
    USER_TYPE_CHOICES = [
        ('citizen', 'Citoyen'),
        ('broker', 'Courtier'),
    ]
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        initial='citizen',
        widget=forms.RadioSelect(attrs={'class': 'hidden'})  # Nous gérons le style dans le template
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition placeholder-gray-400',
            'placeholder': '+223 XX XX XX XX'
        })
    )
    
    location = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition placeholder-gray-400',
            'placeholder': 'Ex: Badalabougou, Hippodrome...'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'location', 'user_type', 'password1', 'password2')
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition placeholder-gray-400',
                'placeholder': 'Choisissez un nom d\'utilisateur'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition placeholder-gray-400',
                'placeholder': 'votre@email.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les champs de mot de passe
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition placeholder-gray-400',
            'placeholder': 'Créez un mot de passe sécurisé'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition placeholder-gray-400',
            'placeholder': 'Confirmez votre mot de passe'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        
        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error('email', 'Un utilisateur avec cet email existe déjà.')
        
        if phone and User.objects.filter(phone__iexact=phone).exists():
            self.add_error('phone', 'Un utilisateur avec ce numéro existe déjà.')
        
        return cleaned_data


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur, Email ou Téléphone",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition placeholder-gray-400',
            'placeholder': 'Entrez votre username, email ou numéro',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition placeholder-gray-400',
            'placeholder': 'Votre mot de passe'
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Vérifier si l'identifiant existe
            user_exists = User.objects.filter(
                Q(username__iexact=username) |
                Q(email__iexact=username) |
                Q(phone__iexact=username)
            ).exists()
            
            if not user_exists:
                raise ValidationError("Aucun compte trouvé avec ces identifiants.")
        
        return username