from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'dashboard'

router = DefaultRouter()
router.register(r'activities', views.ActivityLogViewSet, basename='activity')
router.register(r'preferences', views.DashboardPreferenceViewSet, basename='preference')

urlpatterns = [
    path('stats/', views.DashboardStatsView.as_view(), name='stats'),
    path('', include(router.urls)),
]
