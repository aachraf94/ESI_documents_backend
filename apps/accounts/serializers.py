from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Notification
import random
import string

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that adds user information to the token.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['name'] = f"{user.first_name} {user.last_name}"
        token['email'] = user.email
        token['role'] = user.role
        return token

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data (retrieve, update).
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active']
        read_only_fields = ['id']

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users with automatic password generation.
    """
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role']
    
    def create(self, validated_data):
        """
        Create a new user with a random password that will be emailed to them.
        """
        # Generate a random password
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            password=temp_password,
            temp_password=temp_password
        )
        return user

class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing a user's password.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        """
        Validate the new password using Django's password validators.
        """
        validate_password(value)
        return value

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset.
    """
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a password reset.
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        """
        Validate the new password using Django's password validators.
        """
        validate_password(value)
        return value

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for user notifications.
    """
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'date_created', 'is_read']
        read_only_fields = ['id', 'date_created']
