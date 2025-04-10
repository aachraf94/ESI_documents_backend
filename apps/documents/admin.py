from django.contrib import admin
from .models import Employee, AttestationTravail, OrdreMission, EtapeMission

class EtapeMissionInline(admin.TabularInline):
    model = EtapeMission
    extra = 1

class OrdreMissionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'missionnaire', 'lieu_destination', 'date_depart', 'date_retour', 'date_creation')
    list_filter = ('date_creation', 'moyen_transport')
    search_fields = ('reference', 'missionnaire__first_name', 'missionnaire__last_name', 'lieu_destination')
    inlines = [EtapeMissionInline]

class AttestationTravailAdmin(admin.ModelAdmin):
    list_display = ('reference', 'employee', 'date_emission')
    list_filter = ('date_emission',)
    search_fields = ('reference', 'employee__first_name', 'employee__last_name')

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'grade', 'fonction', 'categorie', 'statut_emploi')
    list_filter = ('categorie', 'statut_emploi', 'grade')
    search_fields = ('last_name', 'first_name', 'grade', 'fonction')
    fieldsets = (
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'date_naissance', 'lieu_naissance')}),
        ('Informations professionnelles', {'fields': ('grade', 'fonction', 'categorie', 'service')}),
        ('Période d\'emploi', {'fields': ('date_embauche', 'date_depart', 'statut_emploi')}),
        ('Pièce d\'identité', {'fields': ('num_piece_identite', 'date_emission_piece', 'lieu_emission_piece')}),
    )

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(AttestationTravail, AttestationTravailAdmin)
admin.site.register(OrdreMission, OrdreMissionAdmin)
