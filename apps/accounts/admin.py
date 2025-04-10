from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Notification

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'temp_password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('temp_password',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'date_created', 'is_read')
    list_filter = ('is_read', 'date_created')
    search_fields = ('user__email', 'message')
    date_hierarchy = 'date_created'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Notification, NotificationAdmin)
