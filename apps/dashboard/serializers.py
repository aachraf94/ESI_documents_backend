from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, extend_schema_field, OpenApiExample
from .models import ActivityLog, DashboardPreference
from apps.accounts.models import CustomUser, Notification
from apps.documents.models import Employee, AttestationTravail, OrdreMission
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Activity Log Example',
            value={
                "id": 1,
                "user": 1,
                "user_name": "Admin User",
                "action_type": "VIEW",
                "action_name": "Consultation",
                "content_type": "EMPLOYEE",
                "content_name": "Employé",
                "content_id": 5,
                "description": "Consultation du profil employé",
                "timestamp": "2023-10-15T14:30:45Z",
                "ip_address": "192.168.1.100"
            }
        )
    ]
)
class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for system activity logs"""
    user_name = serializers.SerializerMethodField()
    action_name = serializers.CharField(source='get_action_type_display')
    content_name = serializers.CharField(source='get_content_type_display')
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_name', 'action_type', 'action_name', 
                  'content_type', 'content_name', 'content_id', 'description', 
                  'timestamp', 'ip_address']
        read_only_fields = ['id', 'timestamp']
    
    @extend_schema_field(serializers.CharField())
    def get_user_name(self, obj) -> str:
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return "System"

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Dashboard Preference Example',
            value={
                "id": 1,
                "user": 1,
                "layout": {"widgets": {"order": ["stats", "recent", "activities"]}},
                "visible_widgets": ["user_stats", "documents_stats", "recent_activities"],
                "date_range": "last_month",
                "updated_at": "2023-10-15T14:30:45Z"
            }
        )
    ]
)
class DashboardPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user dashboard preferences"""
    class Meta:
        model = DashboardPreference
        fields = ['id', 'user', 'layout', 'visible_widgets', 'date_range', 'updated_at']
        read_only_fields = ['id', 'updated_at']

class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics in the dashboard"""
    total_users = serializers.IntegerField(help_text="Nombre total d'utilisateurs dans le système")
    active_users = serializers.IntegerField(help_text="Nombre d'utilisateurs actifs")
    users_by_role = serializers.DictField(child=serializers.IntegerField(), help_text="Répartition des utilisateurs par rôle")
    recent_users = serializers.ListField(child=serializers.DictField(), help_text="Liste des utilisateurs récemment ajoutés")

class DocumentStatsSerializer(serializers.Serializer):
    """Serializer for document statistics in the dashboard"""
    total_employees = serializers.IntegerField(help_text="Nombre total d'employés")
    active_employees = serializers.IntegerField(help_text="Nombre d'employés actifs")
    total_attestations = serializers.IntegerField(help_text="Nombre total d'attestations")
    total_missions = serializers.IntegerField(help_text="Nombre total d'ordres de mission")
    employees_by_category = serializers.DictField(child=serializers.IntegerField(), help_text="Répartition des employés par catégorie")
    recent_attestations = serializers.ListField(child=serializers.DictField(), help_text="Dernières attestations créées")
    recent_missions = serializers.ListField(child=serializers.DictField(), help_text="Derniers ordres de mission créés")
    
class ActivityStatsSerializer(serializers.Serializer):
    """Serializer for activity statistics in the dashboard"""
    activity_by_date = serializers.DictField(child=serializers.IntegerField(), help_text="Activité par date")
    activity_by_type = serializers.DictField(child=serializers.IntegerField(), help_text="Activité par type d'action")
    recent_activities = serializers.ListField(child=serializers.DictField(), help_text="Activités récentes dans le système")

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Dashboard Summary Example',
            value={
                "user_stats": {
                    "total_users": 15,
                    "active_users": 12,
                    "users_by_role": {"ADMIN": 2, "RH": 3, "SG": 7},
                    "recent_users": [
                        {
                            "id": 15,
                            "email": "user15@example.com",
                            "first_name": "Sarah",
                            "last_name": "Lakhel",
                            "role": "RH",
                            "date_joined": "2023-10-12T10:30:00Z"
                        }
                    ]
                },
                "document_stats": {
                    "total_employees": 50,
                    "active_employees": 45,
                    "total_attestations": 30,
                    "total_missions": 25,
                    "employees_by_category": {
                        "ENSEIGNANT": 30,
                        "ADMINISTRATIF": 15,
                        "TECHNIQUE": 5
                    },
                    "recent_attestations": [
                        {
                            "id": 30,
                            "reference": "AT-2023-0030",
                            "employee__first_name": "Ahmed",
                            "employee__last_name": "Benali",
                            "date_emission": "2023-10-14"
                        }
                    ],
                    "recent_missions": [
                        {
                            "id": 25,
                            "reference": "OM-2023-0025",
                            "missionnaire__first_name": "Mohamed",
                            "missionnaire__last_name": "Charef",
                            "lieu_destination": "Paris",
                            "date_creation": "2023-10-13"
                        }
                    ]
                },
                "activity_stats": {
                    "activity_by_date": {
                        "2023-10-14": 25,
                        "2023-10-13": 18,
                        "2023-10-12": 30
                    },
                    "activity_by_type": {
                        "VIEW": 40,
                        "CREATE": 20,
                        "UPDATE": 10,
                        "DELETE": 3
                    },
                    "recent_activities": [
                        {
                            "id": 150,
                            "user__first_name": "Admin",
                            "user__last_name": "User",
                            "action_type": "CREATE",
                            "content_type": "EMPLOYEE",
                            "description": "Création d'un nouvel employé",
                            "timestamp": "2023-10-14T15:30:45Z"
                        }
                    ]
                }
            }
        )
    ]
)
class SummarySerializer(serializers.Serializer):
    """Serializer for complete dashboard summary statistics"""
    user_stats = UserStatsSerializer(help_text="Statistiques des utilisateurs")
    document_stats = DocumentStatsSerializer(help_text="Statistiques des documents")
    activity_stats = ActivityStatsSerializer(help_text="Statistiques des activités")
