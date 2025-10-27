from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

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