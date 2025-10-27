# stations/models.py
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


class Station(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom de la station")
    neighborhood = models.CharField(max_length=100, verbose_name="Quartier")
    description = models.TextField(blank=True, verbose_name="Description (facultatif)")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Stats de confirmation
    is_confirmed = models.BooleanField(default=False)
    last_confirmation = models.DateTimeField(null=True, blank=True)
    confirmation_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_confirmation', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.neighborhood}"

class StationReport(models.Model):
    FUEL_TYPES = [
        ('essence', 'Essence'),
        ('diesel', 'Diesel'),
        ('both', 'Les deux'),
    ]
    
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Signalement
    has_fuel = models.BooleanField(default=True, verbose_name="Carburant disponible")
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPES, default='essence')
    description = models.TextField(blank=True, verbose_name="Commentaire (facultatif)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['station', 'user']  # Un user ne peut signaler qu'une fois par station
    
    def __str__(self):
        status = "🟢 Disponible" if self.has_fuel else "🔴 Rupture"
        return f"{self.station.name} - {status} par {self.user.username}"
