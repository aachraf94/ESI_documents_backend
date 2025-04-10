from rest_framework import serializers
from .models import Employee, AttestationTravail, OrdreMission, EtapeMission

class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for Employee model"""
    class Meta:
        model = Employee
        fields = '__all__'

class AttestationTravailSerializer(serializers.ModelSerializer):
    """Serializer for AttestationTravail model"""
    employee_name = serializers.ReadOnlyField(source='employee.__str__')
    
    class Meta:
        model = AttestationTravail
        fields = ['id', 'reference', 'employee', 'employee_name', 'date_emission', 'emetteur']
        read_only_fields = ['date_emission']

class EtapeMissionSerializer(serializers.ModelSerializer):
    """Serializer for EtapeMission model"""
    class Meta:
        model = EtapeMission
        fields = ['id', 'lieu_depart', 'lieu_arrivee', 'date_depart', 'date_arrivee', 'moyen_transport']
        
class OrdreMissionSerializer(serializers.ModelSerializer):
    """Serializer for OrdreMission model with nested EtapeMission data"""
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
