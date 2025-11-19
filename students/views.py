from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/dashboard.html')

def profile(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/profile.html')

def sessions(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/sessions.html')

def session_material(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/session_material.html')

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