from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = 'document'

# Main router
router = DefaultRouter()
router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'attestations', views.AttestationTravailViewSet, basename='attestation')
router.register(r'missions', views.OrdreMissionViewSet, basename='mission')

# Nested router for mission stages
missions_router = routers.NestedSimpleRouter(
    router, 
    r'missions', 
    lookup='mission',
    trailing_slash=True
)
missions_router.register(
    r'etapes', 
    views.EtapeMissionViewSet, 
    basename='mission-etapes'
)

urlpatterns = [
    path('', include(router.urls)),
    path('', include(missions_router.urls)),
]
