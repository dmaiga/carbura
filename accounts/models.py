from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPES = [
        ('citizen', 'Citoyen'),
        ('broker', 'Courtier'),
        ('admin', 'Admin')
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='citizen')
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=255, blank=True)  # Quartier/Zone
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"