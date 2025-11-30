from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student
from tutoring_sessions.models import Session, Enrollment, SessionMaterial, AdvisingSession
from .forms import AvatarUpdateForm, SupportNeedsUpdateForm
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

@login_required
def dashboard(request):
    """Dashboard cho student - hiển thị today sessions và advising sessions"""
    try:
        student = request.user.student
    except:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('home')
    
    today = timezone.now().date()
    
    # Map Python weekday sang format của database
    weekday_map = {
        0: '2',   # Monday
        1: '3',   # Tuesday
        2: '4',   # Wednesday
        3: '5',   # Thursday
        4: '6',   # Friday
        5: '7',   # Saturday
        6: 'cn',  # Sunday
    }
    
    today_code = weekday_map[today.weekday()]
    
    # Lấy các sessions mà student đã enroll
    enrolled_sessions = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('session', 'session__subject', 'session__tutor')
    
    # Filter sessions hôm nay
    today_sessions = []
    for enrollment in enrolled_sessions:
        session = enrollment.session
        # Chỉ hiển thị sessions đang scheduled hoặc ongoing
        if session.status in ['scheduled', 'ongoing']:
            days_list = session.days.split('-')
            if today_code in days_list:
                today_sessions.append(session)
    
    # Sort theo thời gian
    today_sessions.sort(key=lambda x: x.start_time)
    
    # Lấy advising sessions của các lớp mà student đã enroll
    # Chỉ lấy advising sessions trong 7 ngày tới
    next_week = today + timedelta(days=7)
    
    # Lấy danh sách session IDs mà student đã enroll
    enrolled_session_ids = [e.session.id for e in enrolled_sessions]
    
    # Lấy advising sessions
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
    materials = SessionMaterial.objects.filter(session=session)  # ← Giờ đã có import rồi
    
    return render(request, 'students/session_material.html', {
        'session': session,
        'materials': materials,
    })

def find_sessions(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/find_sessions.html')

def library(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/library.html')

def feedback(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/feedback.html')

def request_session(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/request_session.html')

def technical_report(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/technical_report.html')

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