from rest_framework import viewsets, permissions, status, generics
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

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that includes additional user information in the token payload
    """
    serializer_class = CustomTokenObtainPairSerializer

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
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
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
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific notification as read.
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "notification marked as read"})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all of a user's unread notifications as read.
        """
        notifications = self.get_queryset().filter(is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        return Response({"status": f"{count} notifications marked as read"})
