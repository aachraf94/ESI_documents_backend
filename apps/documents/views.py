from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

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

@extend_schema_view(
    list=extend_schema(
        summary="Liste tous les employés",
        description="Retourne une liste paginée de tous les employés présents dans le système.",
        tags=["Employees"]
    ),
    retrieve=extend_schema(
        summary="Détails d'un employé",
        description="Retourne les informations détaillées d'un employé spécifique.",
        tags=["Employees"]
    ),
    create=extend_schema(
        summary="Créer un employé",
        description="Crée un nouvel employé dans le système.",
        tags=["Employees"],
        examples=[
            OpenApiExample(
                'Example Employee',
                value={
                    "first_name": "Ahmed",
                    "last_name": "Benali",
                    "date_naissance": "1985-03-15",
                    "lieu_naissance": "Alger",
                    "grade": "Ingénieur principal",
                    "fonction": "Chef de service",
                    "categorie": "ADMINISTRATIF",
                    "date_embauche": "2010-09-01",
                    "service": "Informatique",
                    "statut_emploi": "ACTIF"
                }
            )
        ],
        responses={
            201: EmployeeSerializer,
            400: OpenApiResponse(description="Données invalides"),
            403: OpenApiResponse(description="Permissions insuffisantes")
        }
    ),
    update=extend_schema(
        summary="Mettre à jour un employé",
        description="Met à jour les informations d'un employé existant.",
        tags=["Employees"]
    ),
    partial_update=extend_schema(
        summary="Mise à jour partielle d'un employé",
        description="Met à jour partiellement les informations d'un employé.",
        tags=["Employees"]
    ),
    destroy=extend_schema(
        summary="Supprimer un employé",
        description="Supprime un employé du système.",
        tags=["Employees"]
    )
)
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
    
    @extend_schema(
        summary="Employés actifs",
        description="Retourne uniquement les employés avec un statut 'actif'",
        tags=["Employees"],
        responses={200: EmployeeSerializer(many=True)}
    )
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
    
    @extend_schema(
        summary="Employés par catégorie",
        description="Filtre les employés par catégorie professionnelle",
        tags=["Employees"],
        parameters=[
            OpenApiParameter(
                name="category",
                description="Code de catégorie d'employé (ex: ENSEIGNANT, ADMINISTRATIF)",
                required=True,
                type=str
            )
        ],
        responses={
            200: EmployeeSerializer(many=True),
            400: OpenApiResponse(description="Paramètre 'category' manquant")
        }
    )
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

@extend_schema_view(
    list=extend_schema(
        summary="Liste des attestations de travail",
        description="Retourne une liste paginée de toutes les attestations de travail.",
        tags=["Work Certificates"]
    ),
    retrieve=extend_schema(
        summary="Détails d'une attestation",
        description="Retourne les informations détaillées d'une attestation de travail.",
        tags=["Work Certificates"]
    ),
    create=extend_schema(
        summary="Créer une attestation",
        description="Crée une nouvelle attestation de travail avec référence auto-générée.",
        tags=["Work Certificates"],
        examples=[
            OpenApiExample(
                'Example Attestation',
                value={
                    "employee": 1,
                    "emetteur": "Directeur de l'École Nationale Supérieure d'Informatique"
                }
            )
        ],
        responses={
            201: AttestationTravailSerializer,
            400: OpenApiResponse(description="Données invalides"),
            403: OpenApiResponse(description="Permissions insuffisantes")
        }
    ),
    update=extend_schema(
        summary="Mettre à jour une attestation",
        description="Met à jour les informations d'une attestation existante.",
        tags=["Work Certificates"]
    ),
    partial_update=extend_schema(
        summary="Mise à jour partielle d'une attestation",
        description="Met à jour partiellement les informations d'une attestation.",
        tags=["Work Certificates"]
    ),
    destroy=extend_schema(
        summary="Supprimer une attestation",
        description="Supprime une attestation du système.",
        tags=["Work Certificates"]
    )
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
    
    @extend_schema(
        summary="Attestations par employé",
        description="Retourne toutes les attestations de travail d'un employé spécifique",
        tags=["Work Certificates"],
        parameters=[
            OpenApiParameter(
                name="employee_id",
                description="ID de l'employé",
                required=True,
                type=int
            )
        ],
        responses={
            200: AttestationTravailSerializer(many=True),
            400: OpenApiResponse(description="Paramètre 'employee_id' manquant")
        }
    )
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

@extend_schema_view(
    list=extend_schema(
        summary="Liste des ordres de mission",
        description="Retourne une liste paginée de tous les ordres de mission.",
        tags=["Mission Orders"]
    ),
    retrieve=extend_schema(
        summary="Détails d'un ordre de mission",
        description="Retourne les informations détaillées d'un ordre de mission.",
        tags=["Mission Orders"]
    ),
    create=extend_schema(
        summary="Créer un ordre de mission",
        description="Crée un nouvel ordre de mission avec référence auto-générée.",
        tags=["Mission Orders"],
        examples=[
            OpenApiExample(
                'Example Mission Order',
                value={
                    "missionnaire": 1,
                    "objet_mission": "Participation à une conférence internationale",
                    "lieu_destination": "Paris, France",
                    "date_depart": "2023-11-15T08:00:00Z",
                    "date_retour": "2023-11-20T18:00:00Z",
                    "moyen_transport": "AVION",
                    "nuits_hebergement": 5,
                    "duree_mission_jours": 6,
                    "etapes": [
                        {
                            "lieu_depart": "Alger",
                            "lieu_arrivee": "Paris",
                            "date_depart": "2023-11-15T08:00:00Z",
                            "date_arrivee": "2023-11-15T11:00:00Z",
                            "moyen_transport": "AVION"
                        },
                        {
                            "lieu_depart": "Paris",
                            "lieu_arrivee": "Alger",
                            "date_depart": "2023-11-20T14:00:00Z",
                            "date_arrivee": "2023-11-20T18:00:00Z",
                            "moyen_transport": "AVION"
                        }
                    ]
                }
            )
        ],
        responses={
            201: OrdreMissionSerializer,
            400: OpenApiResponse(description="Données invalides"),
            403: OpenApiResponse(description="Permissions insuffisantes")
        }
    ),
    update=extend_schema(
        summary="Mettre à jour un ordre de mission",
        description="Met à jour les informations d'un ordre de mission existant.",
        tags=["Mission Orders"]
    ),
    partial_update=extend_schema(
        summary="Mise à jour partielle d'un ordre de mission",
        description="Met à jour partiellement les informations d'un ordre de mission.",
        tags=["Mission Orders"]
    ),
    destroy=extend_schema(
        summary="Supprimer un ordre de mission",
        description="Supprime un ordre de mission du système.",
        tags=["Mission Orders"]
    )
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
    
    @extend_schema(
        summary="Missions par employé",
        description="Retourne tous les ordres de mission d'un employé spécifique",
        tags=["Mission Orders"],
        parameters=[
            OpenApiParameter(
                name="employee_id",
                description="ID de l'employé",
                required=True,
                type=int
            )
        ],
        responses={
            200: OrdreMissionSerializer(many=True),
            400: OpenApiResponse(description="Paramètre 'employee_id' manquant")
        }
    )
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
    
    @extend_schema(
        summary="Étapes d'une mission",
        description="Retourne toutes les étapes d'un ordre de mission spécifique",
        tags=["Mission Orders"],
        responses={200: EtapeMissionSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def etapes(self, request, pk=None):
        """Get all stages for a specific mission order"""
        ordre_mission = self.get_object()
        etapes = ordre_mission.etapes.all()
        serializer = EtapeMissionSerializer(etapes, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Ajouter une étape à une mission",
        description="Ajoute une nouvelle étape à un ordre de mission existant",
        tags=["Mission Orders"],
        request=EtapeMissionSerializer,
        responses={
            201: EtapeMissionSerializer,
            400: OpenApiResponse(description="Données invalides")
        }
    )
    @etapes.mapping.post
    def add_etape(self, request, pk=None):
        """Add a new stage to a mission order"""
        ordre_mission = self.get_object()
        serializer = EtapeMissionSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(ordre_mission=ordre_mission)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        summary="Liste des étapes de mission",
        description="Retourne une liste de toutes les étapes de mission.",
        tags=["Mission Orders"]
    ),
    retrieve=extend_schema(
        summary="Détails d'une étape",
        description="Retourne les informations détaillées d'une étape de mission.",
        tags=["Mission Orders"]
    ),
    create=extend_schema(
        summary="Créer une étape",
        description="Crée une nouvelle étape de mission.",
        tags=["Mission Orders"],
        examples=[
            OpenApiExample(
                'Example Mission Stage',
                value={
                    "lieu_depart": "Alger",
                    "lieu_arrivee": "Paris",
                    "date_depart": "2023-11-15T08:00:00Z",
                    "date_arrivee": "2023-11-15T11:00:00Z",
                    "moyen_transport": "AVION"
                }
            )
        ],
        responses={
            201: EtapeMissionSerializer,
            400: OpenApiResponse(description="Données invalides")
        }
    ),
    update=extend_schema(
        summary="Mettre à jour une étape",
        description="Met à jour les informations d'une étape de mission existante.",
        tags=["Mission Orders"]
    ),
    partial_update=extend_schema(
        summary="Mise à jour partielle d'une étape",
        description="Met à jour partiellement les informations d'une étape de mission.",
        tags=["Mission Orders"]
    ),
    destroy=extend_schema(
        summary="Supprimer une étape",
        description="Supprime une étape de mission du système.",
        tags=["Mission Orders"]
    )
)
class EtapeMissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing mission stages.
    Typically accessed as a nested resource of mission orders.
    """
    queryset = EtapeMission.objects.all()
    serializer_class = EtapeMissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="mission_pk",
                location=OpenApiParameter.PATH,
                description="ID of the mission order",
                required=True,
                type=int
            )
        ]
    )
    def get_queryset(self):
        """Filter stages by the parent mission order if specified"""
        mission_id = self.kwargs.get('mission_pk')
        if mission_id is not None:
            return EtapeMission.objects.filter(ordre_mission_id=mission_id)
        return EtapeMission.objects.all()
