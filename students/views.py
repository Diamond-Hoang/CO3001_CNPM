from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student
from tutoring_sessions.models import Session, Enrollment, SessionMaterial

@login_required
def dashboard(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/dashboard.html')

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