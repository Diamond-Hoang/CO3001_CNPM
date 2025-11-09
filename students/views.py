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

def find_sessions(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/find_sessions.html')

def library(request):
    if request.user.userprofile.role != 'student':
        return render(request, '403.html', status=403)
    return render(request, 'students/library.html')

