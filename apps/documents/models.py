# apps/dashboard/models.py
from django.db import models

from apps.accounts.models import CustomUser

class Employee(models.Model):
    EMPLOYMENT_STATUS = (
        ('ACTIF', 'Actif'),
        ('DEMISSION', 'Démission'),
        ('RETRAITE', 'Retraite'),
    )
    
    EMPLOYEE_CATEGORY = (
        ('ENSEIGNANT', 'Enseignant/Chercheur'),
        ('ADMINISTRATIF', 'Administratif'),
        ('TECHNIQUE', 'Technique'),
        ('OUVRIER', 'Ouvrier professionnel'),
    )
    
    first_name = models.CharField(verbose_name='Prénom', max_length=50)
    last_name = models.CharField(verbose_name='Nom', max_length=50)
    date_naissance = models.DateField(verbose_name='Date de naissance')
    lieu_naissance = models.CharField(verbose_name='Lieu de naissance', max_length=100)
    grade = models.CharField(verbose_name='Grade', max_length=100)
    fonction = models.CharField(verbose_name='Fonction', max_length=100)
    categorie = models.CharField(
        verbose_name='Catégorie',
        max_length=20,
        choices=EMPLOYEE_CATEGORY,
        default='ADMINISTRATIF'
    )
    date_embauche = models.DateField(verbose_name='Date d\'embauche')
    date_depart = models.DateField(verbose_name='Date de départ', null=True, blank=True)
    service = models.CharField(verbose_name='Service/Département', max_length=100, blank=True)
    statut_emploi = models.CharField(
        verbose_name='Statut d\'emploi',
        max_length=10,
        choices=EMPLOYMENT_STATUS,
        default='ACTIF'
    )
    num_piece_identite = models.CharField(verbose_name='Numéro de pièce d\'identité', max_length=50, blank=True)
    date_emission_piece = models.DateField(verbose_name='Date d\'émission de la pièce d\'identité', null=True, blank=True)
    lieu_emission_piece = models.CharField(verbose_name='Lieu d\'émission de la pièce d\'identité', max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class AttestationTravail(models.Model):
    reference = models.CharField(verbose_name='Référence', max_length=50)
    employee = models.ForeignKey(Employee, verbose_name='Employé', on_delete=models.CASCADE, related_name='attestations')
    date_emission = models.DateField(verbose_name='Date d\'émission', auto_now_add=True)
    emetteur = models.CharField(verbose_name='Émetteur', max_length=100, default="Directeur de l'École Nationale Supérieure d'Informatique")
    
    class Meta:
        verbose_name = 'Attestation de travail'
        verbose_name_plural = 'Attestations de travail'
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Attestation de travail - {self.employee} - {self.date_emission}"

class OrdreMission(models.Model):
    TRANSPORT_CHOICES = (
        ('VOITURE', 'Voiture de service'),
        ('VOITURE_PERSONNELLE', 'Voiture personnelle'),
        ('AVION', 'Avion'),
        ('TRAIN', 'Train'),
        ('TRANSPORT_COMMUN', 'Transport en commun'),
        ('AUTRE', 'Autre'),
    )
    
    reference = models.CharField(verbose_name='Numéro de référence', max_length=50)
    missionnaire = models.ForeignKey(Employee, verbose_name='Missionnaire', on_delete=models.CASCADE, related_name='missions')
    objet_mission = models.TextField(verbose_name='Objet de la mission', max_length=500)
    
    lieu_depart = models.CharField(verbose_name='Lieu de départ', max_length=100, default='Alger')
    lieu_destination = models.CharField(verbose_name='Lieu de destination', max_length=100)
    
    date_depart = models.DateTimeField(verbose_name='Date et heure de départ')
    date_retour = models.DateTimeField(verbose_name='Date et heure de retour')
    
    moyen_transport = models.CharField(
        verbose_name='Moyen de transport',
        max_length=30,
        choices=TRANSPORT_CHOICES
    )
    
    # Informations financières
    avance = models.DecimalField(
        verbose_name='Montant de l\'avance',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    numero_avance = models.CharField(verbose_name='Numéro du relevé d\'avance', max_length=50, blank=True)
    date_avance = models.DateField(verbose_name='Date de l\'avance', null=True, blank=True)
    lieu_avance = models.CharField(verbose_name='Lieu de l\'avance', max_length=100, blank=True)
    
    # Séjour
    nuits_hebergement = models.PositiveSmallIntegerField(verbose_name='Nombre de nuits d\'hébergement', default=0)
    duree_mission_jours = models.PositiveSmallIntegerField(verbose_name='Durée en jours', default=1)
    duree_mission_heures = models.PositiveSmallIntegerField(verbose_name='Durée en heures', default=0)
    
    # Approbations
    date_creation = models.DateField(verbose_name='Date de création', auto_now_add=True)
    responsable_emission = models.CharField(verbose_name='Responsable émetteur', max_length=100)
    
    class Meta:
        verbose_name = 'Ordre de mission'
        verbose_name_plural = 'Ordres de mission'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Mission - {self.missionnaire} - {self.lieu_destination} - {self.date_depart.strftime('%d/%m/%Y')}"

class EtapeMission(models.Model):
    """Modèle pour enregistrer les étapes d'une mission (aller/retour/escales)"""
    ordre_mission = models.ForeignKey(OrdreMission, verbose_name='Ordre de mission', on_delete=models.CASCADE, related_name='etapes')
    lieu_depart = models.CharField(verbose_name='Lieu de départ', max_length=100)
    lieu_arrivee = models.CharField(verbose_name='Lieu d\'arrivée', max_length=100)
    date_depart = models.DateTimeField(verbose_name='Date et heure de départ')
    date_arrivee = models.DateTimeField(verbose_name='Date et heure d\'arrivée')
    moyen_transport = models.CharField(verbose_name='Moyen de transport', max_length=30)
    
    class Meta:
        verbose_name = 'Étape de mission'
        verbose_name_plural = 'Étapes de mission'
        ordering = ['date_depart']
    
    def __str__(self):
        return f"{self.lieu_depart} → {self.lieu_arrivee} ({self.date_depart.strftime('%d/%m/%Y')})"