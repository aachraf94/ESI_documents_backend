"""
URL configuration for ESI_document_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Redirect root URL to Swagger documentation
    path("", RedirectView.as_view(url='/api/schema/swagger/', permanent=True)),
    
    path("admin/", admin.site.urls),
    
    # API Schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # App URLs
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/documents/", include("apps.documents.urls")),
]
