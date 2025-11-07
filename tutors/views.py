from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    if request.user.userprofile.role != 'tutor':
        return render(request, '403.html', status=403)
    return render(request, 'tutors/dashboard.html')
