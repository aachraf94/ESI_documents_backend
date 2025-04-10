from django.db import models
from django.utils import timezone
from apps.accounts.models import CustomUser

class ActivityLog(models.Model):
    """
    Model for tracking user activity in the system
    """
    ACTION_TYPES = (
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('VIEW', 'Consultation'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('OTHER', 'Autre'),
    )
    
    CONTENT_TYPES = (
        ('USER', 'Utilisateur'),
        ('EMPLOYEE', 'Employé'),
        ('ATTESTATION', 'Attestation de travail'),
        ('MISSION', 'Ordre de mission'),
        ('SYSTEM', 'Système'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    content_type = models.CharField(max_length=15, choices=CONTENT_TYPES)
    content_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action_type']),
            models.Index(fields=['content_type']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.email if self.user else "System"
        return f"{user_str} - {self.get_action_type_display()} - {self.timestamp}"

class DashboardPreference(models.Model):
    """
    Model for saving user dashboard preferences
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='dashboard_preference')
    layout = models.JSONField(default=dict)
    visible_widgets = models.JSONField(default=list)
    date_range = models.CharField(max_length=20, default='last_week')
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dashboard preferences for {self.user.email}"

