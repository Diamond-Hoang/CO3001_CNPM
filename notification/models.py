from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ... các model khác ...

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('session_request', 'Session Request'),
        ('session_confirmed', 'Session Confirmed'),
        ('session_cancelled', 'Session Cancelled'),
        ('session_completed', 'Session Completed'),
        ('announcement', 'Announcement'),
        ('feedback_received', 'Feedback Received'),
        ('technical_report', 'Technical Report'),
    ]
    
    # Recipient (Observer)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True,
        blank=True,
        help_text="Specific user (null = broadcast to all)"
    )
    
    # Notification content
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects (optional)
    session_id = models.IntegerField(null=True, blank=True, help_text="Related session ID")
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_broadcast = models.BooleanField(default=False, help_text="Broadcast to all users")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # URL to redirect when clicked
    action_url = models.CharField(max_length=500, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['is_broadcast', '-created_at']),
        ]
    
    def __str__(self):
        recipient = self.user.username if self.user else "ALL USERS"
        return f"{self.notification_type} → {recipient}: {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class NotificationObserver(models.Model):
    """Observer registration for specific events"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_subscriptions')
    event_type = models.CharField(max_length=30)
    session_id = models.IntegerField(null=True, blank=True, help_text="Subscribe to specific session")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user', 'event_type', 'session_id']]
        verbose_name = 'Notification Observer'
        verbose_name_plural = 'Notification Observers'
    
    def __str__(self):
        session_info = f" (Session {self.session_id})" if self.session_id else ""
        return f"{self.user.username} observing {self.event_type}{session_info}"