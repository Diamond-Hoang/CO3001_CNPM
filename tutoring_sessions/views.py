from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Session, Enrollment, SessionMaterial, Feedback
from students.models import Student

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
    enrollment.delete()
    return redirect('students:sessions')

@login_required
def feedback(request, enrollment_id):
    """Gửi feedback"""
    student = get_object_or_404(Student, user=request.user)
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=student)
    
    if enrollment.session.status != 'completed':
        messages.error(request, 'Chỉ có thể feedback khi session đã hoàn thành')
        return redirect('students:sessions')
    
    if hasattr(enrollment, 'feedback'):
        messages.info(request, 'Bạn đã feedback session này rồi')
        return redirect('students:sessions')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        would_recommend = request.POST.get('would_recommend') == 'on'
        
        Feedback.objects.create(
            enrollment=enrollment,
            rating=rating,
            comment=comment,
            would_recommend=would_recommend
        )
        
        messages.success(request, 'Cảm ơn bạn đã gửi feedback!')
        return redirect('students:sessions')
    
    return render(request, 'students/feedback.html', {
        'enrollment': enrollment,
    })

@login_required
def available_sessions(request):
    """Các session có thể đăng ký"""
    student = get_object_or_404(Student, user=request.user)
    
    enrolled_session_ids = Enrollment.objects.filter(
        student=student, 
        is_active=True
    ).values_list('session_id', flat=True)
    
    sessions = Session.objects.exclude(
        id__in=enrolled_session_ids
    ).filter(
        status='scheduled'
    ).select_related('subject', 'tutor')
    
    return render(request, 'tutoring_sessions/available_sessions.html', {
        'sessions': sessions,
    })

@login_required
def enroll_session(request, session_id):
    """Đăng ký session mới"""
    student = get_object_or_404(Student, user=request.user)
    session = get_object_or_404(Session, id=session_id)
    
    if session.is_full:
        messages.error(request, 'Session đã đầy')
        return redirect('tutoring_sessions:available_sessions')
    
    if Enrollment.objects.filter(student=student, session=session, is_active=True).exists():
        messages.info(request, 'Bạn đã đăng ký session này rồi')
        return redirect('students:my_sessions')
    
    if request.method == 'POST':
        Enrollment.objects.create(student=student, session=session)
        
        session.enrolled_count += 1
        session.save()
        
        messages.success(request, f'Đăng ký session {session.class_code} thành công!')
        return redirect('students:my_sessions')
    
    return render(request, 'tutoring_sessions/enroll_confirm.html', {
        'session': session,
    })