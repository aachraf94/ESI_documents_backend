from rest_framework import serializers
from .models import ActivityLog, DashboardPreference
from apps.accounts.models import CustomUser, Notification
from apps.documents.models import Employee, AttestationTravail, OrdreMission
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    action_name = serializers.CharField(source='get_action_type_display')
    content_name = serializers.CharField(source='get_content_type_display')
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_name', 'action_type', 'action_name', 
                  'content_type', 'content_name', 'content_id', 'description', 
                  'timestamp', 'ip_address']
        read_only_fields = ['id', 'timestamp']
    
    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return "System"

class DashboardPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardPreference
        fields = ['id', 'user', 'layout', 'visible_widgets', 'date_range', 'updated_at']
        read_only_fields = ['id', 'updated_at']

class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    users_by_role = serializers.DictField(child=serializers.IntegerField())
    recent_users = serializers.ListField(child=serializers.DictField())

class DocumentStatsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    total_attestations = serializers.IntegerField()
    total_missions = serializers.IntegerField()
    employees_by_category = serializers.DictField(child=serializers.IntegerField())
    recent_attestations = serializers.ListField(child=serializers.DictField())
    recent_missions = serializers.ListField(child=serializers.DictField())
    
class ActivityStatsSerializer(serializers.Serializer):
    activity_by_date = serializers.DictField(child=serializers.IntegerField())
    activity_by_type = serializers.DictField(child=serializers.IntegerField())
    recent_activities = serializers.ListField(child=serializers.DictField())

class SummarySerializer(serializers.Serializer):
    user_stats = UserStatsSerializer()
    document_stats = DocumentStatsSerializer()
    activity_stats = ActivityStatsSerializer()
