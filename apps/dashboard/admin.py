from django.contrib import admin
from .models import ActivityLog, DashboardPreference

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action_type', 'content_type', 'timestamp', 'description')
    list_filter = ('action_type', 'content_type', 'timestamp')
    search_fields = ('user__email', 'description')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

@admin.register(DashboardPreference)
class DashboardPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_range', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('updated_at',)
