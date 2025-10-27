from django.utils import timezone
from datetime import timedelta
# stations/services.py
def check_auto_confirmation(station):
    """
    Vérifie si une station peut être confirmée automatiquement
    3 signalements positifs en moins de 4 heures
    """
    four_hours_ago = timezone.now() - timedelta(hours=4)
    
    # Compter les signalements récents positifs
    recent_positive_reports = station.reports.filter(
        has_fuel=True,
        created_at__gte=four_hours_ago
    )
    
    if recent_positive_reports.count() >= 3:
        # Confirmer la station
        station.is_confirmed = True
        station.last_confirmation = timezone.now()
        station.confirmation_count += 1
        station.save()
        return True
    
    return False