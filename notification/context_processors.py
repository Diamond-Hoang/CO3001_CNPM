from notification.notification_service import NotificationService

    
def notifications(request):
    """Add notifications to all template contexts"""
    if request.user.is_authenticated:
        notifications = NotificationService.get_user_notifications(request.user)
        unread_count = NotificationService.get_unread_count(request.user)
        
        return {
            'user_notifications': notifications[:5],  # Latest 5
            'unread_count': unread_count,
        }
    return {
        'user_notifications': [],
        'unread_count': 0,
    }