from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tutoring_sessions.models import Enrollment, Session
from students.models import Student
from .models import Feedback
from .forms import SessionRequestForm, TechnicalReportForm
from django.db.models import Avg

# Create your views here.
@login_required
def feedback(request, enrollment_id):
    """Submit feedback for a completed session"""
    student = get_object_or_404(Student, user=request.user)
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=student)
    
    # Check if the session is completed
    if enrollment.session.status != 'completed':
        messages.error(request, 'Feedback can only be submitted when the session is completed.')
        return redirect('students:sessions')
    
    # Check if feedback already exists (assuming OneToOneField from Enrollment to Feedback)
    if hasattr(enrollment, 'feedback'):
        messages.info(request, 'You have already submitted feedback for this session.')
        return redirect('students:sessions')
    
    if request.method == 'POST':
        # Simple POST data processing (assuming fields are 'rating' and 'comment')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        Feedback.objects.create(
            enrollment=enrollment,
            rating=rating,
            comment=comment,
        )
        
        messages.success(request, 'Thank you for submitting your feedback!')
        return redirect('students:sessions')
    
    return render(request, 'students/feedback.html', {
        'enrollment': enrollment,
    })

@login_required
def request_session(request):
    """View to submit a new session request from a student"""
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
    
    # Specify the app containing the template
    return render(request, 'students/request_session.html', {'form': form})

@login_required
def technical_report(request):
    """View to submit a technical report"""

    # 🔥 Select base template based on role
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
        'dashboard_url': dashboard_url,  # 🔥 Pass to template
    })

@login_required
def view_feedback(request, session_id):
    """
    View to display all feedback for a specific session.
    Only accessible by the tutor of that session.
    """
    # Get session and verify it belongs to the logged-in tutor
    session = get_object_or_404(Session, id=session_id, tutor=request.user.tutor)
    
    # Get all enrollments for this session
    enrollments = Enrollment.objects.filter(session=session).select_related(
        'student', 'student__user'
    )
    
    # Separate enrollments with and without comments for display
    feedbacks_with_comments = []
    feedbacks_without_comments = [] # This holds ratings without detailed comments
    
    for enrollment in enrollments:
        try:
            feedback = enrollment.feedback # Access the related Feedback object
            if feedback.comment:
                feedbacks_with_comments.append({
                    'student': enrollment.student,
                    'rating': feedback.rating,
                    'comment': feedback.comment,
                    'created_at': feedback.created_at
                })
            else:
                feedbacks_without_comments.append({
                    'student': enrollment.student,
                    'rating': feedback.rating,
                    'created_at': feedback.created_at
                })
        except Feedback.DoesNotExist:
            # Student hasn't submitted feedback yet
            pass
    
    # Calculate statistics
    all_feedbacks = Feedback.objects.filter(enrollment__session=session)
    total_feedbacks = all_feedbacks.count()
    total_students = enrollments.count()
    
    stats = {
        # Calculate average rating
        'average_rating': all_feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0,
        'total_feedbacks': total_feedbacks,
        'total_students': total_students,
        # Calculate feedback submission rate
        'feedback_rate': (total_feedbacks / total_students * 100) if total_students > 0 else 0,
        # Calculate rating distribution
        'rating_distribution': {
            5: all_feedbacks.filter(rating=5).count(),
            4: all_feedbacks.filter(rating=4).count(),
            3: all_feedbacks.filter(rating=3).count(),
            2: all_feedbacks.filter(rating=2).count(),
            1: all_feedbacks.filter(rating=1).count(),
        }
    }
    
    context = {
        'session': session,
        'feedbacks_with_comments': feedbacks_with_comments,
        'feedbacks_without_comments': feedbacks_without_comments,
        'stats': stats,
    }
    
    return render(request, 'feedback/view_feedback.html', context)