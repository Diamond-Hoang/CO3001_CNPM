from django.contrib.auth.models import User
from .models import Notification, NotificationObserver
from django.urls import reverse
from typing import List, Optional


class NotificationService:
    """
    Observer Pattern Implementation for Notifications
    This service acts as the Subject that notifies all registered observers
    """
    
    @staticmethod
    def notify(
        notification_type: str,
        title: str,
        message: str,
        recipients: Optional[List[User]] = None,
        session_id: Optional[int] = None,
        action_url: str = "",
        related_object_id: Optional[int] = None,
        related_object_type: Optional[str] = None,
        is_broadcast: bool = False
    ):
        """
        Main notification method - notifies observers based on criteria
        
        Args:
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            recipients: Specific users to notify (if None and not broadcast, uses observers)
            session_id: Related session ID
            action_url: URL to redirect when notification is clicked
            related_object_id: ID of related object
            related_object_type: Type of related object
            is_broadcast: If True, notify ALL users
        """
        
        if is_broadcast:
            # Broadcast to all users
            return NotificationService._create_broadcast_notification(
                notification_type, title, message, session_id, action_url
            )
        
        if recipients:
            # Notify specific users
            return NotificationService._notify_users(
                recipients, notification_type, title, message, 
                session_id, action_url, related_object_id, related_object_type
            )
        
        if session_id:
            # Get observers for this session
            observers = NotificationObserver.objects.filter(
                event_type=notification_type,
                session_id=session_id,
                is_active=True
            )
            recipients = [obs.user for obs in observers]
            return NotificationService._notify_users(
                recipients, notification_type, title, message,
                session_id, action_url, related_object_id, related_object_type
            )
        
        # Get general observers for this event type
        observers = NotificationObserver.objects.filter(
            event_type=notification_type,
            session_id__isnull=True,
            is_active=True
        )
        recipients = [obs.user for obs in observers]
        return NotificationService._notify_users(
            recipients, notification_type, title, message,
            session_id, action_url, related_object_id, related_object_type
        )
    
    @staticmethod
    def _notify_users(
        users: List[User],
        notification_type: str,
        title: str,
        message: str,
        session_id: Optional[int],
        action_url: str,
        related_object_id: Optional[int],
        related_object_type: Optional[str]
    ):
        """Create individual notifications for specific users"""
        notifications = []
        for user in users:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                session_id=session_id,
                action_url=action_url,
                related_object_id=related_object_id,
                related_object_type=related_object_type,
                is_broadcast=False
            )
            notifications.append(notification)
        return notifications
    
    @staticmethod
    def _create_broadcast_notification(
        notification_type: str,
        title: str,
        message: str,
        session_id: Optional[int],
        action_url: str
    ):
        """Create a broadcast notification for all users"""
        return Notification.objects.create(
            user=None,  # null = broadcast
            notification_type=notification_type,
            title=title,
            message=message,
            session_id=session_id,
            action_url=action_url,
            is_broadcast=True
        )
    
    # Helper methods for specific events
    
    @staticmethod
    def notify_session_request_created(session_request, tutors: List[User]):
        """Notify all tutors when a new session request is created"""
        return NotificationService.notify(
            notification_type='session_request',
            title='New Session Request',
            message=f'{session_request.student.username} requested a session: {session_request.subject}',
            recipients=tutors,
            session_id=session_request.id,
            action_url=f'/tutor/session-requests/{session_request.id}/',
            related_object_id=session_request.id,
            related_object_type='SessionRequest'
        )
    
    @staticmethod
    def notify_session_confirmed(session, student: User):
        """Notify student when their session is confirmed"""
        return NotificationService.notify(
            notification_type='session_confirmed',
            title='Session Confirmed',
            message=f'Your session "{session.title}" has been confirmed for {session.date}',
            recipients=[student],
            session_id=session.id,
            action_url=f'/student/sessions/{session.id}/',
            related_object_id=session.id,
            related_object_type='Session'
        )
    
    @staticmethod
    def notify_session_completed(session, participants: List[User]):
        """Notify all participants when session is completed"""
        return NotificationService.notify(
            notification_type='session_completed',
            title='Session Completed',
            message=f'Session "{session.title}" has been completed. Please provide feedback.',
            recipients=participants,
            session_id=session.id,
            action_url=f'/student/sessions/{session.id}/feedback/',
            related_object_id=session.id,
            related_object_type='Session'
        )
    
    @staticmethod
    def broadcast_announcement(title: str, message: str):
        """Broadcast announcement to all users"""
        return NotificationService.notify(
            notification_type='announcement',
            title=title,
            message=message,
            is_broadcast=True
        )
    
    @staticmethod
    def subscribe_to_session(user: User, session_id: int, event_type: str = 'session_completed'):
        """Subscribe user to notifications for a specific session"""
        observer, created = NotificationObserver.objects.get_or_create(
            user=user,
            event_type=event_type,
            session_id=session_id,
            defaults={'is_active': True}
        )
        return observer
    
    @staticmethod
    def unsubscribe_from_session(user: User, session_id: int, event_type: str):
        """Unsubscribe user from session notifications"""
        NotificationObserver.objects.filter(
            user=user,
            event_type=event_type,
            session_id=session_id
        ).update(is_active=False)
    
    @staticmethod
    def get_user_notifications(user: User, unread_only: bool = False):
        """Get notifications for a specific user (including broadcasts)"""
        # Personal notifications
        personal = Notification.objects.filter(user=user)
        
        # Broadcast notifications
        broadcasts = Notification.objects.filter(is_broadcast=True)
        
        # Combine
        notifications = personal | broadcasts
        
        if unread_only:
            notifications = notifications.filter(is_read=False)
        
        return notifications.order_by('-created_at')
    
    @staticmethod
    def get_unread_count(user: User):
        """Get count of unread notifications"""
        personal_unread = Notification.objects.filter(user=user, is_read=False).count()
        broadcast_unread = Notification.objects.filter(is_broadcast=True, is_read=False).count()
        return personal_unread + broadcast_unread