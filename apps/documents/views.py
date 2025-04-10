from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Employee, AttestationTravail, OrdreMission, EtapeMission
from .serializers import (
    EmployeeSerializer,
    AttestationTravailSerializer,
    OrdreMissionSerializer,
    EtapeMissionSerializer
)
from datetime import datetime
import uuid

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access a view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing employees.
    Only admin users can perform CRUD operations.
    """
    queryset = Employee.objects.all().order_by('last_name', 'first_name')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'grade', 'fonction', 'service']
    ordering_fields = ['last_name', 'first_name', 'date_embauche', 'grade']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active employees"""
        active_employees = Employee.objects.filter(statut_emploi='ACTIF')
        page = self.paginate_queryset(active_employees)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(active_employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get employees grouped by category"""
        category = request.query_params.get('category', None)
        if category:
            employees = Employee.objects.filter(categorie=category)
            serializer = self.get_serializer(employees, many=True)
            return Response(serializer.data)
        return Response(
            {"detail": "Parameter 'category' is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

class AttestationTravailViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing work certificates.
    Authenticated users can perform CRUD operations.
    """
    queryset = AttestationTravail.objects.all().order_by('-date_emission')
    serializer_class = AttestationTravailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['employee__first_name', 'employee__last_name', 'reference']
    ordering_fields = ['date_emission', 'reference']
    
    def perform_create(self, serializer):
        """Generate a unique reference number when creating a new attestation"""
        today = datetime.today()
        # Format: AT-{YEAR}-{sequential number}
        existing_count = AttestationTravail.objects.filter(
            date_emission__year=today.year
        ).count()
        reference = f"AT-{today.year}-{existing_count + 1:04d}"
        serializer.save(reference=reference)
    
    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Get attestations for a specific employee"""
        employee_id = request.query_params.get('employee_id', None)
        if employee_id:
            attestations = AttestationTravail.objects.filter(employee_id=employee_id)
            serializer = self.get_serializer(attestations, many=True)
            return Response(serializer.data)
        return Response(
            {"detail": "Parameter 'employee_id' is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

class OrdreMissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing mission orders.
    Authenticated users can perform CRUD operations.
    """
    queryset = OrdreMission.objects.all().order_by('-date_creation')
    serializer_class = OrdreMissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['missionnaire__first_name', 'missionnaire__last_name', 
                     'reference', 'lieu_destination', 'objet_mission']
    ordering_fields = ['date_creation', 'date_depart', 'reference']
    
    def perform_create(self, serializer):
        """Generate a unique reference number when creating a new ordre de mission"""
        today = datetime.today()
        # Format: OM-{YEAR}-{sequential number}
        existing_count = OrdreMission.objects.filter(
            date_creation__year=today.year
        ).count()
        reference = f"OM-{today.year}-{existing_count + 1:04d}"
        serializer.save(reference=reference, responsable_emission=f"{self.request.user.first_name} {self.request.user.last_name}")
    
    @action(detail=False, methods=['get'])
    def by_employee(self, request):
        """Get missions for a specific employee"""
        employee_id = request.query_params.get('employee_id', None)
        if employee_id:
            missions = OrdreMission.objects.filter(missionnaire_id=employee_id)
            serializer = self.get_serializer(missions, many=True)
            return Response(serializer.data)
        return Response(
            {"detail": "Parameter 'employee_id' is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['get'])
    def etapes(self, request, pk=None):
        """Get all stages for a specific mission order"""
        ordre_mission = self.get_object()
        etapes = ordre_mission.etapes.all()
        serializer = EtapeMissionSerializer(etapes, many=True)
        return Response(serializer.data)
    
    @etapes.mapping.post
    def add_etape(self, request, pk=None):
        """Add a new stage to a mission order"""
        ordre_mission = self.get_object()
        serializer = EtapeMissionSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(ordre_mission=ordre_mission)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EtapeMissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing mission stages.
    Typically accessed as a nested resource of mission orders.
    """
    queryset = EtapeMission.objects.all()
    serializer_class = EtapeMissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter stages by the parent mission order if specified"""
        mission_id = self.kwargs.get('mission_pk')
        if mission_id is not None:
            return EtapeMission.objects.filter(ordre_mission_id=mission_id)
        return EtapeMission.objects.all()
