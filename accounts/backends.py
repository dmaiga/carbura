from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class MultiFieldAuthBackend(ModelBackend):
    """
    Authentifie l'utilisateur via username, email ou phone
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username')
        
        if username is None or password is None:
            return None
        
        try:
            # Chercher l'utilisateur par username, email ou phone
            user = User.objects.get(
                Q(username__iexact=username) |
                Q(email__iexact=username) |
                Q(phone__iexact=username)
            )
        except User.DoesNotExist:
            # Retourner None si aucun utilisateur n'est trouvé
            return None
        except User.MultipleObjectsReturned:
            # En cas de doublon, prendre le premier
            user = User.objects.filter(
                Q(username__iexact=username) |
                Q(email__iexact=username) |
                Q(phone__iexact=username)
            ).first()
        
        # Vérifier le mot de passe
        if user and user.check_password(password):
            return user
        
        return None