from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import Employee, AttestationTravail, OrdreMission, EtapeMission

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Employee Example',
            summary='Employee Information',
            value={
                "id": 1,
                "first_name": "Ahmed",
                "last_name": "Benali",
                "date_naissance": "1985-03-15",
                "lieu_naissance": "Alger",
                "grade": "Ingénieur principal",
                "fonction": "Chef de service",
                "categorie": "ADMINISTRATIF",
                "date_embauche": "2010-09-01",
                "date_depart": None,
                "service": "Informatique",
                "statut_emploi": "ACTIF",
                "num_piece_identite": "123456789",
                "date_emission_piece": "2015-05-10",
                "lieu_emission_piece": "Alger"
            }
        )
    ]
)
class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model - contains complete employee information"""
    class Meta:
        model = Employee
        fields = '__all__'

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Work Certificate Example',
            summary='Attestation de travail',
            value={
                "id": 1,
                "reference": "AT-2023-0001",
                "employee": 1,
                "employee_name": "Benali Ahmed",
                "date_emission": "2023-10-15",
                "emetteur": "Directeur de l'École Nationale Supérieure d'Informatique"
            }
        )
    ]
)
class AttestationTravailSerializer(serializers.ModelSerializer):
    """Serializer for AttestationTravail model - work certificates issued to employees"""
    employee_name = serializers.ReadOnlyField(source='employee.__str__')
    
    class Meta:
        model = AttestationTravail
        fields = ['id', 'reference', 'employee', 'employee_name', 'date_emission', 'emetteur']
        read_only_fields = ['date_emission']

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Mission Stage Example',
            summary='Étape d\'une mission',
            value={
                "id": 1,
                "lieu_depart": "Alger",
                "lieu_arrivee": "Paris",
                "date_depart": "2023-11-15T08:00:00Z",
                "date_arrivee": "2023-11-15T11:00:00Z",
                "moyen_transport": "AVION"
            }
        )
    ]
)
class EtapeMissionSerializer(serializers.ModelSerializer):
    """Serializer for EtapeMission model - defines a leg of a mission journey"""
    class Meta:
        model = EtapeMission
        fields = ['id', 'lieu_depart', 'lieu_arrivee', 'date_depart', 'date_arrivee', 'moyen_transport']
        
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Mission Order Example',
            summary='Ordre de mission',
            value={
                "id": 1,
                "reference": "OM-2023-0001",
                "missionnaire": 1,
                "missionnaire_name": "Benali Ahmed",
                "objet_mission": "Participation à une conférence internationale",
                "lieu_depart": "Alger",
                "lieu_destination": "Paris, France",
                "date_depart": "2023-11-15T08:00:00Z",
                "date_retour": "2023-11-20T18:00:00Z",
                "moyen_transport": "AVION",
                "avance": "1500.00",
                "numero_avance": "AV-2023-047",
                "date_avance": "2023-11-01",
                "lieu_avance": "Alger",
                "nuits_hebergement": 5,
                "duree_mission_jours": 6,
                "duree_mission_heures": 0,
                "date_creation": "2023-10-15",
                "responsable_emission": "Bentaleb Karima",
                "etapes": [
                    {
                        "id": 1,
                        "lieu_depart": "Alger",
                        "lieu_arrivee": "Paris",
                        "date_depart": "2023-11-15T08:00:00Z",
                        "date_arrivee": "2023-11-15T11:00:00Z",
                        "moyen_transport": "AVION"
                    },
                    {
                        "id": 2,
                        "lieu_depart": "Paris",
                        "lieu_arrivee": "Alger",
                        "date_depart": "2023-11-20T14:00:00Z",
                        "date_arrivee": "2023-11-20T18:00:00Z",
                        "moyen_transport": "AVION"
                    }
                ]
            }
        )
    ]
)
class OrdreMissionSerializer(serializers.ModelSerializer):
    """Serializer for OrdreMission model with nested EtapeMission data - mission orders for employees"""
    etapes = EtapeMissionSerializer(many=True, required=False)
    missionnaire_name = serializers.ReadOnlyField(source='missionnaire.__str__')
    
    class Meta:
        model = OrdreMission
        fields = '__all__'
        read_only_fields = ['date_creation']
    
    def create(self, validated_data):
        etapes_data = validated_data.pop('etapes', [])
        ordre_mission = OrdreMission.objects.create(**validated_data)
        
        for etape_data in etapes_data:
            EtapeMission.objects.create(ordre_mission=ordre_mission, **etape_data)
            
        return ordre_mission
    
    def update(self, instance, validated_data):
        etapes_data = validated_data.pop('etapes', None)
        
        # Update the main OrdreMission fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create related EtapeMission objects if provided
        if etapes_data is not None:
            instance.etapes.all().delete()  # Remove existing etapes
            for etape_data in etapes_data:
                EtapeMission.objects.create(ordre_mission=instance, **etape_data)
                
        return instance
