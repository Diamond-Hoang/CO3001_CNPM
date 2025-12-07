# notification/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification
from .notification_service import NotificationService


@login_required
def notifications_list(request):
    """View to display all notifications, setting the correct base template based on user role"""
    # 🔥 Select base template based on role
    if request.user.userprofile.role == 'tutor':
        base_template = 'tutor_base.html'
        dashboard_url = 'tutors:tutor_dashboard'
    else:
        base_template = 'student_base.html'
        dashboard_url = 'students:student_dashboard'
    
    notifications = NotificationService.get_user_notifications(request.user)
    unread_count = NotificationService.get_unread_count(request.user)
    
    return render(request, 'notification/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'base_template': base_template,
        'dashboard_url': dashboard_url,
    })


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id)
        # Check if the notification belongs to the user or is a broadcast
        if notification.user == request.user or notification.is_broadcast:
            notification.mark_as_read()
            return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        pass
    # Return 404 if not found or unauthorized (though unauthorized check is implicit via notification.user)
    return JsonResponse({'success': False}, status=404)


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read for the current user"""
    # Only update notifications explicitly addressed to the current user
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})