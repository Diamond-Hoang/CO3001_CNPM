from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student
from tutoring_sessions.models import Session, Enrollment, SessionMaterial, AdvisingSession
from .forms import AvatarUpdateForm, SupportNeedsUpdateForm
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, F

@login_required
def dashboard(request):
    """Dashboard for student - display today sessions and advising sessions"""
    try:
        student = request.user.student
    except:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    today = timezone.now().date()
    
    # Map Python weekday to database format
    weekday_map = {
        0: 'Monday',    # Monday
        1: 'Tuesday',   # Tuesday
        2: 'Wednesday', # Wednesday
        3: 'Thursday',  # Thursday
        4: 'Friday',    # Friday
        5: 'Saturday',  # Saturday
        6: 'Sunday',    # Sunday
    }
    
    today_code = weekday_map[today.weekday()]
    
    # Get sessions that the student has enrolled in
    enrolled_sessions = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('session', 'session__subject', 'session__tutor')
    
    # Filter today's sessions
    today_sessions = []
    for enrollment in enrolled_sessions:
        session = enrollment.session
        # Only show sessions that are 'scheduled' or 'ongoing'
        if session.status in ['scheduled', 'ongoing']:
            days_list = session.days.split('-')
            if today_code in days_list:
                today_sessions.append(session)
    
    # Sort by time
    today_sessions.sort(key=lambda x: x.start_time)
    
    # Get advising sessions for the classes the student has enrolled in
    # Only retrieve advising sessions within the next 7 days
    next_week = today + timedelta(days=7)
    
    # Get a list of session IDs that the student has enrolled in
    enrolled_session_ids = [e.session.id for e in enrolled_sessions]
    
    # Get advising sessions
    upcoming_advising = AdvisingSession.objects.filter(
        main_session_id__in=enrolled_session_ids,
        date__gte=today,
        date__lte=next_week,
        is_active=True
    ).select_related('main_session', 'main_session__subject', 'tutor').order_by('date', 'start_time')
    
    # Session colors
    colors = ['blue', 'green', 'mint', 'pink', 'peach', 'purple', 'orange', 'teal']
    
    context = {
        'today_sessions': today_sessions,
        'upcoming_advising': upcoming_advising,
        'colors': colors,
        'today': today,
    }
    return render(request, 'students/dashboard.html', context)

def profile(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    student = Student.objects.get(user=request.user)
    return render(request, 'students/profile.html', {'student': student})

def sessions(request):
    enrollments = Enrollment.objects.filter(
        student=request.user.student,
        is_active=True
    ).select_related('session', 'session__subject', 'session__tutor').order_by('-enrolled_at')
    
    return render(request, 'students/sessions.html', {
        'enrollments': enrollments,
    })

@login_required
def session_material(request, session_id):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    
    session = get_object_or_404(Session, id=session_id)
    materials = SessionMaterial.objects.filter(session=session)  # ← Now imported
    
    return render(request, 'students/session_material.html', {
        'session': session,
        'materials': materials,
    })

@login_required
def update_avatar(request):
    if request.method == 'POST':
        student = request.user.student
        form = AvatarUpdateForm(request.POST, request.FILES, instance=student)
        
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'avatar_url': student.avatar.url if student.avatar else None
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def update_support_needs(request):
    if request.method == 'POST':
        student = request.user.student
        form = SupportNeedsUpdateForm(request.POST, instance=student)
        
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'sp_needs': student.sp_needs
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)