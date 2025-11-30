from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tutoring_sessions.models import Enrollment
from students.models import Student
from .models import Feedback, SessionRequest
from .forms import SessionRequestForm, TechnicalReportForm

# Create your views here.
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
        
        Feedback.objects.create(
            enrollment=enrollment,
            rating=rating,
            comment=comment,
        )
        
        messages.success(request, 'Cảm ơn bạn đã gửi feedback!')
        return redirect('students:sessions')
    
    return render(request, 'students/feedback.html', {
        'enrollment': enrollment,
    })

@login_required
def request_session(request):
    if request.method == 'POST':
        form = SessionRequestForm(request.POST)
        if form.is_valid():
            session_request = form.save(commit=False)
            session_request.student = request.user.student
            session_request.save()
            messages.success(request, 'Your session request has been submitted successfully!')
            return redirect('feedback:request_session')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SessionRequestForm()
    
    # Chỉ định rõ app chứa template
    return render(request, 'students/request_session.html', {'form': form})

@login_required
def technical_report(request):
    """View để submit technical report"""

    # 🔥 Chọn base template dựa vào role
    if request.user.userprofile.role == 'tutor':
        base_template = 'tutor_base.html'
        dashboard_url = 'tutors:tutor_dashboard'
    else:
        base_template = 'student_base.html'
        dashboard_url = 'students:student_dashboard'

    if request.method == 'POST':
        form = TechnicalReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()

            messages.success(
                request,
                'Technical issue report sent! Thank you for reporting. We will process it as soon as possible.'
            )
            return redirect('feedback:technical_report')
        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = TechnicalReportForm()

    return render(request, 'feedback/technical_report.html', {
        'form': form,
        'base_template': base_template,
        'dashboard_url': dashboard_url,   # 🔥 Gửi xuống template
    })
