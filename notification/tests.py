# notification/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from notification.models import Notification, NotificationObserver
from notification.notification_service import NotificationService


class NotificationModelTests(TestCase):
    """Test Notification model"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_create_personal_notification(self):
        """Test creating a personal notification"""
        notification = Notification.objects.create(
            user=self.user1,
            notification_type='session_confirmed',
            title='Test Notification',
            message='This is a test message',
        )
        
        self.assertEqual(notification.user, self.user1)
        self.assertEqual(notification.title, 'Test Notification')
        self.assertFalse(notification.is_read)
        self.assertFalse(notification.is_broadcast)
    
    def test_create_broadcast_notification(self):
        """Test creating a broadcast notification"""
        notification = Notification.objects.create(
            user=None,
            notification_type='announcement',
            title='Broadcast Test',
            message='This is a broadcast',
            is_broadcast=True
        )
        
        self.assertIsNone(notification.user)
        self.assertTrue(notification.is_broadcast)
    
    def test_mark_as_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            user=self.user1,
            notification_type='announcement',
            title='Test',
            message='Test message'
        )
        
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)
        
        notification.mark_as_read()
        
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)
    
    def test_notification_str(self):
        """Test notification string representation"""
        notification = Notification.objects.create(
            user=self.user1,
            notification_type='session_confirmed',
            title='Test',
            message='Test'
        )
        
        self.assertIn('session_confirmed', str(notification))
        self.assertIn(self.user1.username, str(notification))


class NotificationServiceTests(TestCase):
    """Test NotificationService"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user('user1', password='pass123')
        self.user2 = User.objects.create_user('user2', password='pass123')
    
    def test_notify_single_user(self):
        """Test notifying a single user"""
        notifications = NotificationService.notify(
            notification_type='session_confirmed',
            title='Session Confirmed',
            message='Your session is confirmed',
            recipients=[self.user1]
        )
        
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].user, self.user1)
        self.assertEqual(notifications[0].title, 'Session Confirmed')
    
    def test_notify_multiple_users(self):
        """Test notifying multiple users"""
        notifications = NotificationService.notify(
            notification_type='session_cancelled',
            title='Session Cancelled',
            message='Session has been cancelled',
            recipients=[self.user1, self.user2]
        )
        
        self.assertEqual(len(notifications), 2)
        users = [n.user for n in notifications]
        self.assertIn(self.user1, users)
        self.assertIn(self.user2, users)
    
    def test_broadcast_announcement(self):
        """Test broadcasting announcement"""
        notification = NotificationService.broadcast_announcement(
            title='System Maintenance',
            message='System will be down'
        )
        
        self.assertIsNotNone(notification)
        self.assertTrue(notification.is_broadcast)
        self.assertIsNone(notification.user)
    
    def test_get_user_notifications(self):
        """Test getting user notifications"""
        # Create personal notification
        NotificationService.notify(
            notification_type='session_confirmed',
            title='Personal',
            message='Personal message',
            recipients=[self.user1]
        )
        
        # Create broadcast
        NotificationService.broadcast_announcement(
            title='Broadcast',
            message='Broadcast message'
        )
        
        # Get user1 notifications
        notifications = NotificationService.get_user_notifications(self.user1)
        
        # Should have 2 (1 personal + 1 broadcast)
        self.assertEqual(notifications.count(), 2)
    
    def test_get_unread_count(self):
        """Test getting unread count"""
        # Create 3 notifications for user1
        NotificationService.notify(
            notification_type='announcement',
            title='Test 1',
            message='Message 1',
            recipients=[self.user1]
        )
        NotificationService.notify(
            notification_type='announcement',
            title='Test 2',
            message='Message 2',
            recipients=[self.user1]
        )
        NotificationService.broadcast_announcement('Test 3', 'Message 3')
        
        # All should be unread
        count = NotificationService.get_unread_count(self.user1)
        self.assertEqual(count, 3)
        
        # Mark one as read
        notification = Notification.objects.filter(user=self.user1).first()
        notification.mark_as_read()
        
        # Should have 2 unread now
        count = NotificationService.get_unread_count(self.user1)
        self.assertEqual(count, 2)
    
    def test_unread_only_filter(self):
        """Test filtering only unread notifications"""
        # Create 2 notifications
        n1 = NotificationService.notify(
            notification_type='announcement',
            title='Test 1',
            message='Message 1',
            recipients=[self.user1]
        )[0]
        
        NotificationService.notify(
            notification_type='announcement',
            title='Test 2',
            message='Message 2',
            recipients=[self.user1]
        )
        
        # Mark one as read
        n1.mark_as_read()
        
        # Get only unread
        unread = NotificationService.get_user_notifications(self.user1, unread_only=True)
        self.assertEqual(unread.count(), 1)


class NotificationViewTests(TestCase):
    """Test notification views"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test notifications
        self.notification1 = Notification.objects.create(
            user=self.user,
            notification_type='session_confirmed',
            title='Test Notification 1',
            message='Message 1'
        )
        self.notification2 = Notification.objects.create(
            user=self.user,
            notification_type='announcement',
            title='Test Notification 2',
            message='Message 2'
        )
    
    def test_notifications_list_view(self):
        """Test notifications list view"""
        response = self.client.get(reverse('notification:notifications_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')
        self.assertContains(response, 'Test Notification 1')
        self.assertContains(response, 'Test Notification 2')
    
    def test_notifications_list_requires_login(self):
        """Test that notifications list requires login"""
        self.client.logout()
        response = self.client.get(reverse('notification:notifications_list'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_mark_notification_read(self):
        """Test marking notification as read"""
        self.assertFalse(self.notification1.is_read)
        
        response = self.client.post(
            reverse('notification:mark_notification_read', 
                   kwargs={'notification_id': self.notification1.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        
        # Reload from database
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
    
    def test_mark_all_read(self):
        """Test marking all notifications as read"""
        response = self.client.post(reverse('notification:mark_all_read'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        
        # Check all notifications are read
        unread_count = Notification.objects.filter(
            user=self.user, 
            is_read=False
        ).count()
        self.assertEqual(unread_count, 0)


class NotificationObserverTests(TestCase):
    """Test Observer pattern implementation"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user('testuser', password='pass123')
    
    def test_create_observer(self):
        """Test creating an observer"""
        observer = NotificationObserver.objects.create(
            user=self.user,
            event_type='session_completed',
            session_id=1,
            is_active=True
        )
        
        self.assertEqual(observer.user, self.user)
        self.assertEqual(observer.event_type, 'session_completed')
        self.assertEqual(observer.session_id, 1)
        self.assertTrue(observer.is_active)
    
    def test_observer_unique_constraint(self):
        """Test unique constraint on observer"""
        NotificationObserver.objects.create(
            user=self.user,
            event_type='session_completed',
            session_id=1
        )
        
        # Try to create duplicate
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            NotificationObserver.objects.create(
                user=self.user,
                event_type='session_completed',
                session_id=1
            )