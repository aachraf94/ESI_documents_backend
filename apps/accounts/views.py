from rest_framework import viewsets, permissions, status, generics, serializers as drf_serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    CustomTokenObtainPairSerializer, 
    UserSerializer, 
    UserCreateSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    NotificationSerializer
)
from .models import Notification

User = get_user_model()

@extend_schema(
    tags=["Authentication"],
    summary="Obtenir un token d'authentification",
    description="Authentifie un utilisateur et retourne un token JWT avec refresh token",
    examples=[
        OpenApiExample(
            "Login Example",
            value={"email": "admin@example.com", "password": "password123"}
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Tokens d'authentification",
            response={
                "type": "object",
                "properties": {
                    "refresh": {"type": "string", "description": "Token de rafraîchissement"},
                    "access": {"type": "string", "description": "Token d'accès JWT"}
                }
            }
        ),
        401: OpenApiResponse(description="Identifiants invalides")
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that includes additional user information in the token payload
    """
    serializer_class = CustomTokenObtainPairSerializer

@extend_schema_view(
    list=extend_schema(
        summary="Liste des utilisateurs",
        description="Retourne une liste des utilisateurs (admin uniquement) ou l'utilisateur courant.",
        tags=["Authentication"]
    ),
    retrieve=extend_schema(
        summary="Détails d'un utilisateur",
        description="Retourne les informations détaillées d'un utilisateur spécifique.",
        tags=["Authentication"],
        parameters=[
            OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH, description="ID de l'utilisateur")
        ]
    ),
    create=extend_schema(
        summary="Créer un utilisateur",
        description="Crée un nouvel utilisateur dans le système et envoie un email avec mot de passe temporaire.",
        tags=["Authentication"],
        examples=[
            OpenApiExample(
                'Example User',
                value={
                    "email": "user@example.com",
                    "first_name": "Mohamed",
                    "last_name": "Charef",
                    "role": "RH"
                }
            )
        ],
        responses={
            201: OpenApiResponse(description="Utilisateur créé avec succès"),
            400: OpenApiResponse(description="Données invalides"),
            403: OpenApiResponse(description="Permissions insuffisantes")
        }
    ),
    update=extend_schema(
        summary="Mettre à jour un utilisateur",
        description="Met à jour les informations d'un utilisateur existant.",
        tags=["Authentication"],
        parameters=[
            OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH, description="ID de l'utilisateur")
        ]
    ),
    partial_update=extend_schema(
        summary="Mise à jour partielle d'un utilisateur",
        description="Met à jour partiellement les informations d'un utilisateur.",
        tags=["Authentication"],
        parameters=[
            OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH, description="ID de l'utilisateur")
        ]
    ),
    destroy=extend_schema(
        summary="Supprimer un utilisateur",
        description="Supprime un utilisateur du système.",
        tags=["Authentication"],
        parameters=[
            OpenApiParameter(name="id", type=int, location=OpenApiParameter.PATH, description="ID de l'utilisateur")
        ]
    )
)
class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing user accounts with role-based permissions.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return all users for admins, only the current user for others.
        """
        if self.request.user.role == 'ADMIN':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        """
        Use different serializers for create vs update/retrieve operations.
        """
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new user and send them an email with their temporary password.
        """
        # Only ADMINs can create users
        if request.user.role != 'ADMIN':
            return Response(
                {"detail": "Vous n'avez pas la permission de créer des utilisateurs."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send email with temporary password
        subject = 'Bienvenue sur le système de gestion de documents ESI'
        message = f"""
        Bonjour {user.first_name} {user.last_name},
        
        Un compte a été créé pour vous sur le système de gestion de documents ESI.
        
        Vos identifiants de connexion:
        Email: {user.email}
        Mot de passe temporaire: {user.temp_password}
        
        Veuillez changer votre mot de passe lors de votre première connexion.
        
        Cordialement,
        L'équipe ESI Document
        """
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error but don't expose it to the client
            print(f"Failed to send email: {str(e)}")
        
        return Response(
            {"detail": "Utilisateur créé avec succès et email envoyé avec le mot de passe."},
            status=status.HTTP_201_CREATED
        )
    
@extend_schema(
    summary="Changer le mot de passe",
    description="Change le mot de passe d'un utilisateur (soi-même ou en tant qu'admin pour un autre utilisateur)",
    tags=["Authentication"],
    request=PasswordChangeSerializer,
    responses={
        200: OpenApiResponse(description="Mot de passe changé avec succès"),
        400: OpenApiResponse(description="Mot de passe incorrect ou invalide"),
        403: OpenApiResponse(description="Permissions insuffisantes")
    }
)
@action(detail=True, methods=['post'], url_path='change_password', permission_classes=[permissions.IsAuthenticated])
def change_password(self, request, pk=None):
    """
    Change a user's password with appropriate permission checks.
    """
    user = self.get_object()
    
    # Only the user themself or an admin can change the password
    if request.user.id != user.id and request.user.role != 'ADMIN':
        return Response(
            {"detail": "Vous n'avez pas la permission de changer ce mot de passe."},
            status=status.HTTP_403_FORBIDDEN
        )
        
    serializer = PasswordChangeSerializer(data=request.data)
    if serializer.is_valid():
        # If admin is changing someone else's password, don't require old password
        if request.user.role == 'ADMIN' and request.user.id != user.id:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Mot de passe changé avec succès."})
        
        # Otherwise, verify old password
        if user.check_password(serializer.validated_data['old_password']):
            user.set_password(serializer.validated_data['new_password'])
            # Clear any temporary password
            user.temp_password = None
            user.save()
            return Response({"detail": "Mot de passe changé avec succès."})
        else:
            return Response(
                {"old_password": ["Mot de passe incorrect."]}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Authentication"],
    summary="Demander réinitialisation mot de passe",
    description="Envoie un email contenant un token de réinitialisation à l'adresse email fournie",
    request=PasswordResetRequestSerializer,
    responses={
        200: OpenApiResponse(description="Instructions envoyées (si l'adresse existe)"),
        500: OpenApiResponse(description="Erreur lors de l'envoi de l'email")
    }
)
class PasswordResetRequestView(generics.GenericAPIView):
    """
    Request a password reset by providing an email address.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create a combined token for the reset URL
            combined_token = f"{uid}-{token}"
            
            subject = 'Réinitialisation de votre mot de passe ESI Document'
            message = f"""
            Bonjour {user.first_name} {user.last_name},
            
            Vous avez demandé une réinitialisation de votre mot de passe.
            Veuillez utiliser le jeton suivant pour réinitialiser votre mot de passe:
            
            {combined_token}
            
            Ce jeton est valide pour 24 heures.
            
            Cordialement,
            L'équipe ESI Document
            """
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send password reset email: {str(e)}")
                return Response(
                    {"detail": "Erreur lors de l'envoi de l'email. Veuillez réessayer plus tard."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response(
                {"detail": "Instructions de réinitialisation envoyées à votre adresse email."},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            # For security reasons, don't disclose that the email doesn't exist
            return Response(
                {"detail": "Si l'adresse existe, les instructions de réinitialisation ont été envoyées."},
                status=status.HTTP_200_OK
            )

@extend_schema(
    tags=["Authentication"],
    summary="Confirmer réinitialisation mot de passe",
    description="Réinitialise le mot de passe de l'utilisateur à l'aide d'un token valide",
    request=PasswordResetConfirmSerializer,
    responses={
        200: OpenApiResponse(description="Mot de passe réinitialisé avec succès"),
        400: OpenApiResponse(description="Token invalide ou expiré")
    }
)
class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Confirm a password reset using a token and set a new password.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            combined_token = serializer.validated_data['token']
            
            # More robust token parsing that handles different formats
            if '-' not in combined_token:
                return Response(
                    {"detail": "Format de jeton invalide."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            uid, token = combined_token.split('-', 1)
            
            # Decode the user ID
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            # Check if token is valid
            if not default_token_generator.check_token(user, token):
                return Response(
                    {"detail": "Le jeton de réinitialisation est invalide ou a expiré."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Set the new password
            user.set_password(serializer.validated_data['new_password'])
            # Clear any temporary password
            user.temp_password = None
            user.save()
            
            return Response(
                {"detail": "Mot de passe réinitialisé avec succès."},
                status=status.HTTP_200_OK
            )
        except (TypeError, ValueError) as e:
            return Response(
                {"detail": f"Erreur de format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Utilisateur non trouvé."},
                status=status.HTTP_400_BAD_REQUEST
            )

@extend_schema(
    tags=["Authentication"],
    summary="Déconnexion",
    description="Déconnecte un utilisateur en ajoutant son refresh token à la blacklist",
    request=drf_serializers.Serializer({"refresh": drf_serializers.CharField()}),
    responses={
        200: OpenApiResponse(description="Déconnexion réussie"),
        400: OpenApiResponse(description="Token invalid ou expiré")
    }
)
class LogoutView(generics.GenericAPIView):
    """
    Logout a user by blacklisting their refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Le jeton de rafraîchissement est requis."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Déconnexion réussie."},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"detail": "Le jeton fourni est invalide ou expiré."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (KeyError, TypeError, ValueError):
            return Response(
                {"detail": "Format de jeton invalide."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Erreur lors de la déconnexion: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema_view(
    list=extend_schema(
        summary="Liste des notifications",
        description="Retourne les notifications de l'utilisateur connecté",
        tags=["Notifications"]
    ),
    retrieve=extend_schema(
        summary="Détails d'une notification",
        description="Retourne les détails d'une notification spécifique.",
        tags=["Notifications"],
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la notification")
        ]
    ),
    create=extend_schema(
        summary="Créer une notification",
        description="Crée une nouvelle notification et envoie un email à l'utilisateur.",
        tags=["Notifications"],
        examples=[
            OpenApiExample(
                'Example Notification',
                value={
                    "user": 1,
                    "message": "Votre attestation de travail est prête"
                }
            )
        ],
        responses={
            201: NotificationSerializer,
            400: OpenApiResponse(description="Données invalides")
        }
    ),
    update=extend_schema(
        summary="Mettre à jour une notification",
        description="Met à jour une notification existante.",
        tags=["Notifications"],
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la notification")
        ]
    ),
    partial_update=extend_schema(
        summary="Mise à jour partielle d'une notification",
        description="Met à jour partiellement une notification existante.",
        tags=["Notifications"],
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la notification")
        ]
    ),
    destroy=extend_schema(
        summary="Supprimer une notification",
        description="Supprime une notification du système.",
        tags=["Notifications"],
        parameters=[
            OpenApiParameter(name="id", type=OpenApiTypes.INT, location=OpenApiParameter.PATH, description="ID de la notification")
        ]
    )
)
class NotificationViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing user notifications with appropriate permissions.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Users can only see their own notifications.
        """
        return Notification.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create a notification and send an email.
        """
        notification = serializer.save()
        
        # Send email notification
        subject = 'Nouvelle notification sur ESI Document'
        message = f"""
        Bonjour {notification.user.first_name} {notification.user.last_name},
        
        Vous avez reçu une nouvelle notification:
        
        {notification.message}
        
        Cordialement,
        L'équipe ESI Document
        """
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [notification.user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send notification email: {str(e)}")
    
    @extend_schema(
        summary="Marquer comme lu",
        description="Marque une notification spécifique comme lue",
        tags=["Notifications"],
        responses={200: OpenApiResponse(description="Notification marquée comme lue")}
    )
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific notification as read.
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "notification marked as read"})
    
    @extend_schema(
        summary="Tout marquer comme lu",
        description="Marque toutes les notifications non lues de l'utilisateur comme lues",
        tags=["Notifications"],
        responses={200: OpenApiResponse(description="Notifications marquées comme lues")}
    )
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all of a user's unread notifications as read.
        """
        notifications = self.get_queryset().filter(is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        return Response({"status": f"{count} notifications marked as read"})
