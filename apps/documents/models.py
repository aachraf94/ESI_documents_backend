# apps/dashboard/models.py
from django.db import models

from apps.accounts.models import CustomUser

class Employee(models.Model):
    EMPLOYMENT_STATUS = (
        ('ACTIF', 'Actif'),
        ('DEMISSION', 'Démission'),
        ('RETRAITE', 'Retraite'),
    )
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee')
    date_naissance = models.DateField(verbose_name='Date de naissance')
    lieu_naissance = models.CharField(verbose_name='Lieu de naissance', max_length=100)
    rotba = models.CharField(verbose_name='Grade', max_length=50)
    wadifa = models.CharField(verbose_name='Fonction', max_length=100)
    date_embauche = models.DateField(verbose_name='Date d\'embauche')
    date_depart = models.DateField(verbose_name='Date de départ', null=True, blank=True)
    statut_emploi = models.CharField(
        verbose_name='Statut d\'emploi',
        max_length=10,
        choices=EMPLOYMENT_STATUS,
        default='ACTIF'
    )
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class AttestationTravail(models.Model):
    employee = models.ForeignKey(Employee, verbose_name='الموظف', on_delete=models.CASCADE)
    date_emission = models.DateTimeField(verbose_name='تاريخ الإصدار', auto_now_add=True)

class OrdreMission(models.Model):
    TRANSPORT_CHOICES = (
        ('VOITURE', 'سيارة'),
        ('AVION', 'طائرة'),
        ('TRAIN', 'قطار'),
    )
    
    titre = models.CharField(verbose_name='العنوان', max_length=200)
    missionaire = models.ForeignKey(Employee, verbose_name='المكلف بالمهمة', on_delete=models.CASCADE)
    date_depart = models.DateTimeField(verbose_name='تاريخ الذهاب')
    date_retour = models.DateTimeField(verbose_name='تاريخ الرجوع')
    moyen_transport = models.CharField(
        verbose_name='وسائل النقل',
        max_length=20,
        choices=TRANSPORT_CHOICES
    )
    avance = models.DecimalField(
        verbose_name='المبلغ المسبق',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    approuve_par = models.ForeignKey(
        CustomUser,
        verbose_name='تمت الموافقة بواسطة',
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'SG'}
    )
    template = models.ForeignKey(
        'DocumentTemplate',
        verbose_name='النموذج',
        on_delete=models.SET_NULL,
        null=True
    )

class Destination(models.Model):
    ordre_mission = models.ForeignKey(OrdreMission, verbose_name='أمر المهمة', on_delete=models.CASCADE)
    lieu_depart = models.CharField(verbose_name='مكان المغادرة', max_length=100)
    lieu_arrivee = models.CharField(verbose_name='مكان الوصول', max_length=100)
    date_depart = models.DateTimeField(verbose_name='تاريخ المغادرة')
    date_arrivee = models.DateTimeField(verbose_name='تاريخ الوصول')

class DocumentTemplate(models.Model):
    TYPE_CHOICES = (
        ('ATTESTATION', 'شهادة عمل'),
        ('MISSION', 'أمر مهمة'),
    )
    
    nom = models.CharField(verbose_name='اسم النموذج', max_length=100)
    type = models.CharField(verbose_name='النوع', max_length=20, choices=TYPE_CHOICES)
    contenu = models.TextField(verbose_name='المحتوى')
    date_creation = models.DateTimeField(verbose_name='تاريخ الإنشاء', auto_now_add=True)

class GeneratedDocument(models.Model):
    TYPE_CHOICES = (
        ('ATTESTATION', 'شهادة عمل'),
        ('MISSION', 'أمر مهمة'),
    )
    
    type = models.CharField(verbose_name='النوع', max_length=20, choices=TYPE_CHOICES)
    template = models.ForeignKey(DocumentTemplate, verbose_name='النموذج', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='المحتوى المولد')
    date_generation = models.DateTimeField(verbose_name='تاريخ التوليد', auto_now_add=True)
    related_attestation = models.OneToOneField(
        AttestationTravail,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    related_mission = models.OneToOneField(
        OrdreMission,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )