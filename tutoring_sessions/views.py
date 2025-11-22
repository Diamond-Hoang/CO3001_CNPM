from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from .models import Session, Enrollment
from students.models import Student
from feedback.models import Feedback


@login_required
def session_list(request):
    """Hiển thị danh sách sessions của student"""
    student = get_object_or_404(Student, user=request.user)
    
    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('session', 'session__subject', 'session__tutor')
    
    return render(request, 'tutoring_sessions/session_list.html', {
        'enrollments': enrollments,
    })

@login_required
def session_detail(request, session_id):
    """Chi tiết session"""
    session = get_object_or_404(Session, id=session_id)
    return render(request, 'tutoring_sessions/session_detail.html', {
        'session': session,
    })

@login_required
def session_materials(request, session_id):
    """Tài liệu của session"""
    session = get_object_or_404(Session, id=session_id)
    materials = session.materials.all()
    return render(request, 'tutoring_sessions/session_materials.html', {
        'session': session,
        'materials': materials,
    })

@login_required
def cancel_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user.student)
    session=enrollment.session
    enrollment.delete()
    
    if session.enrolled_count > 0:
        session.enrolled_count -= 1
        session.save()
    return redirect('students:sessions')

@login_required
def available_sessions(request):
    """Hiển thị các session còn chỗ"""
    student = get_object_or_404(Student, user=request.user)
    
    # Lấy các session mà student đã enroll
    enrolled_session_ids = Enrollment.objects.filter(
        student=student, 
        is_active=True
    ).values_list('session_id', flat=True)
    
    # Lấy các session còn chỗ và chưa enroll
    available_sessions = Session.objects.filter(
        status='scheduled',
    ).exclude(
        id__in=enrolled_session_ids
    ).select_related('subject', 'tutor').order_by('class_code')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        available_sessions = available_sessions.filter(
            Q(class_code__icontains=search_query) |
            Q(subject__name__icontains=search_query) |
            Q(subject__code__icontains=search_query) |
            Q(tutor__full_name__icontains=search_query)
        )
    
    context = {
        'sessions': available_sessions,
        'search_query': search_query,
    }

    return render(request, 'students/find_sessions.html', context)

@login_required
def enroll_session(request, session_id):
    """Tham gia vào session"""
    if request.method != 'POST':
        return redirect('tutoring_sessions:available_sessions')
    
    student = get_object_or_404(Student, user=request.user)
    session = get_object_or_404(Session, id=session_id)
    
    # Kiểm tra session còn chỗ không
    if session.enrolled_count >= session.capacity:
        messages.error(request, 'Session đã đầy, không thể tham gia!')
        return redirect('tutoring_sessions:available_sessions')
    
    # Kiểm tra status
    if session.status != 'scheduled':
        messages.error(request, 'Chỉ có thể tham gia session đang scheduled!')
        return redirect('tutoring_sessions:available_sessions')
    
    # Kiểm tra đã enroll chưa
    if Enrollment.objects.filter(student=student, session=session, is_active=True).exists():
        messages.warning(request, 'Bạn đã tham gia session này rồi!')
        return redirect('tutoring_sessions:available_sessions')
    
    # Tạo enrollment
    Enrollment.objects.create(
        student=student,
        session=session,
        is_active=True
    )
    
    # Tăng enrolled_count
    session.enrolled_count += 1
    session.save()
    
    messages.success(request, f'Đã tham gia thành công vào {session.class_code}!')
    return redirect('students:sessions')