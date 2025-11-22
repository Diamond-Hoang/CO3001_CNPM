from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tutoring_sessions.models import Enrollment
from students.models import Student
from .models import Feedback

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