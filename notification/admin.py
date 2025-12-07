# notification/admin.py
from django.contrib import admin
from .models import Notification, NotificationObserver


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'title', 'is_read', 'is_broadcast', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_broadcast', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at', 'read_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('session_id', 'related_object_id', 'related_object_type', 'action_url'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'is_broadcast', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notification(s) marked as read.')
    mark_as_read.short_description = "Mark selected as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notification(s) marked as unread.')
    mark_as_unread.short_description = "Mark selected as unread"


@admin.register(NotificationObserver)
class NotificationObserverAdmin(admin.ModelAdmin):
    list_display = ['user', 'event_type', 'session_id', 'is_active', 'created_at']
    list_filter = ['event_type', 'is_active']
    search_fields = ['user__username']