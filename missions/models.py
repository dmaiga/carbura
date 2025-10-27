from django.db import models
from django.conf import settings
# accounts/models.py
class Mission(models.Model):
    STATUS_CHOICES = [
        ('pending', '🟡 En attente'),
        ('accepted', '🔵 Acceptée'),
        ('in_progress', '🟠 En cours'),
        ('completed', '✅ Terminée'),
        ('cancelled', '🔴 Annulée'),
    ]
    
    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='missions_as_citizen')
    broker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='missions_as_broker')
    station = models.ForeignKey('stations.Station', on_delete=models.CASCADE)
    
    # Détails de la mission
    fuel_type = models.CharField(max_length=20, default='essence')
    quantity = models.FloatField(default=10.0, verbose_name="Quantité (litres)")
    special_instructions = models.TextField(blank=True, verbose_name="Instructions spéciales")
    
    # Statut et suivi
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Prix convenu")
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Évaluation
    rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, verbose_name="Avis du client")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Mission #{self.id} - {self.station.name} - {self.get_status_display()}"

class MissionApplication(models.Model):
    """Candidatures des courtiers pour une mission"""
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='applications')
    broker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(blank=True, verbose_name="Message au client")
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['mission', 'broker']
    
    def __str__(self):
        return f"Candidature de {self.broker.username} pour Mission #{self.mission.id}"