from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
import json

from apps.accounts.models import CustomUser, Notification
from apps.documents.models import Employee, AttestationTravail, OrdreMission
from .models import ActivityLog, DashboardPreference
from .serializers import (
    ActivityLogSerializer,
    DashboardPreferenceSerializer,
    UserStatsSerializer,
    DocumentStatsSerializer,
    ActivityStatsSerializer,
    SummarySerializer
)

class IsAdminOrRHUser(permissions.BasePermission):
    """
    Custom permission to only allow admin or HR users to access dashboards
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['ADMIN', 'RH']

class ActivityLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for activity logs with role-based permissions.
    """
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminOrRHUser]
    
    def get_queryset(self):
        queryset = ActivityLog.objects.all()
        
        # Filter by user if requested
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by action_type if requested
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Filter by content_type if requested
        content_type = self.request.query_params.get('content_type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset
        
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get only recent activity (last 7 days)"""
        recent_date = timezone.now() - timedelta(days=7)
        activities = ActivityLog.objects.filter(timestamp__gte=recent_date)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)

class DashboardPreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for dashboard preferences
    """
    serializer_class = DashboardPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DashboardPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DashboardStatsView(generics.GenericAPIView):
    """
    API endpoint for dashboard statistics
    """
    permission_classes = [IsAdminOrRHUser]
    
    def get(self, request):
        # Get the date range filter
        days = int(request.query_params.get('days', 30))
        from_date = timezone.now() - timedelta(days=days)
        
        # User stats
        total_users = CustomUser.objects.count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        users_by_role = dict(
            CustomUser.objects.values('role')
                            .annotate(count=Count('id'))
                            .values_list('role', 'count')
        )
        recent_users = list(
            CustomUser.objects.filter(date_joined__gte=from_date)
                            .values('id', 'email', 'first_name', 'last_name', 'role', 'date_joined')
                            .order_by('-date_joined')[:5]
        )
        
        user_stats = {
            'total_users': total_users,
            'active_users': active_users,
            'users_by_role': users_by_role,
            'recent_users': recent_users
        }
        
        # Document stats
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(statut_emploi='ACTIF').count()
        total_attestations = AttestationTravail.objects.count()
        total_missions = OrdreMission.objects.count()
        
        employees_by_category = dict(
            Employee.objects.values('categorie')
                          .annotate(count=Count('id'))
                          .values_list('categorie', 'count')
        )
        
        recent_attestations = list(
            AttestationTravail.objects.filter(date_emission__gte=from_date)
                                    .values('id', 'reference', 'employee__first_name', 'employee__last_name', 'date_emission')
                                    .order_by('-date_emission')[:5]
        )
        
        recent_missions = list(
            OrdreMission.objects.filter(date_creation__gte=from_date)
                              .values('id', 'reference', 'missionnaire__first_name', 'missionnaire__last_name', 
                                     'lieu_destination', 'date_creation')
                              .order_by('-date_creation')[:5]
        )
        
        document_stats = {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'total_attestations': total_attestations,
            'total_missions': total_missions,
            'employees_by_category': employees_by_category,
            'recent_attestations': recent_attestations,
            'recent_missions': recent_missions
        }
        
        # Activity stats
        activity_by_date = dict(
            ActivityLog.objects.filter(timestamp__gte=from_date)
                             .annotate(date=TruncDate('timestamp'))
                             .values('date')
                             .annotate(count=Count('id'))
                             .values_list('date', 'count')
        )
        # Convert date keys to string for serialization
        activity_by_date = {date.strftime('%Y-%m-%d'): count for date, count in activity_by_date.items()}
        
        activity_by_type = dict(
            ActivityLog.objects.filter(timestamp__gte=from_date)
                             .values('action_type')
                             .annotate(count=Count('id'))
                             .values_list('action_type', 'count')
        )
        
        recent_activities = list(
            ActivityLog.objects.filter(timestamp__gte=from_date)
                             .values('id', 'user__first_name', 'user__last_name', 
                                    'action_type', 'content_type', 'description', 'timestamp')
                             .order_by('-timestamp')[:10]
        )
        
        activity_stats = {
            'activity_by_date': activity_by_date,
            'activity_by_type': activity_by_type,
            'recent_activities': recent_activities
        }
        
        # Combine all statistics
        summary = {
            'user_stats': user_stats,
            'document_stats': document_stats,
            'activity_stats': activity_stats
        }
        
        serializer = SummarySerializer(summary)
        return Response(serializer.data)

def log_activity(user, action_type, content_type, content_id=None, description="", request=None):
    """
    Helper function to log user activity
    """
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
        
    ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        content_type=content_type,
        content_id=content_id,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )
