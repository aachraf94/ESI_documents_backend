from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """Custom user model with email as the username field"""
    username = None  # Remove username field
    email = models.EmailField(_('Email'), unique=True, db_index=True)
    first_name = models.CharField(_('Prénom'), max_length=30)
    last_name = models.CharField(_('Nom'), max_length=30)
    
    ROLE_CHOICES = (
        ('ADMIN', 'Administrateur'),
        ('RH', 'Resources Humaines'),
        ('SG', 'Secrétaire Général'),
    )
    role = models.CharField(_('Rôle'), max_length=10, choices=ROLE_CHOICES, db_index=True)
    temp_password = models.CharField(_('Mot de passe temporaire'), max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        indexes = [
            models.Index(fields=['email', 'role']),
        ]

class Notification(models.Model):
    """Model for user notifications"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_('Utilisateur'))
    message = models.TextField(_('Message'))
    date_created = models.DateTimeField(_('Date de création'), auto_now_add=True, db_index=True)
    is_read = models.BooleanField(_('Lu'), default=False, db_index=True)

    class Meta:
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['user', 'date_created']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user}: {self.message[:30]}..."