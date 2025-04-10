from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrateur'),
        ('RH', 'Resources Humaines'),
        ('SG', 'Secrétaire Général'),
    )
    
    # Override default fields for French
    username = None
    first_name = models.CharField(verbose_name='Prénom', max_length=30)
    last_name = models.CharField(verbose_name='Nom', max_length=30)
    email = models.EmailField(verbose_name='Email', unique=True, db_index=True)
    role = models.CharField(verbose_name='Rôle', max_length=10, choices=ROLES, db_index=True)
    temp_password = models.CharField(verbose_name='Mot de passe temporaire', max_length=100, null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        indexes = [
            models.Index(fields=['email', 'role']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


# notifications
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='Utilisateur', on_delete=models.CASCADE, db_index=True)
    message = models.TextField(verbose_name='Message')
    date_created = models.DateTimeField(verbose_name='Date de création', auto_now_add=True, db_index=True)
    is_read = models.BooleanField(verbose_name='Lu', default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date_created']),
            models.Index(fields=['user', 'is_read']),
        ]
        ordering = ['-date_created']

    def __str__(self):
        return f"Notification pour {self.user.email}"