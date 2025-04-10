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
    email = models.EmailField(verbose_name='Email', unique=True)
    role = models.CharField(verbose_name='Rôle', max_length=10, choices=ROLES)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


# notifications
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name='Utilisateur', on_delete=models.CASCADE)
    message = models.TextField(verbose_name='Message')
    date_created = models.DateTimeField(verbose_name='Date de création', auto_now_add=True)
    is_read = models.BooleanField(verbose_name='Lu', default=False)

    def __str__(self):
        return f"Notification pour {self.user.email}"