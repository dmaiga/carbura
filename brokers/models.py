# brokers/models.py
from django.db import models
from django.conf import settings
class Broker(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='broker_profile')
    is_available = models.BooleanField(default=True)
    rating = models.FloatField(default=5.0)
    completed_missions = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)  # Approuvé par l'admin
    description = models.TextField(blank=True, verbose_name="Description du service")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-rating', '-completed_missions']
    
    def __str__(self):
        return f"Courtier: {self.user.username}"
