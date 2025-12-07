from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from .models import Session, Enrollment, SessionMaterial
from students.models import Student
from feedback.models import Feedback


@login_required
def session_list(request):
    """Display the list of sessions for a student"""
    student = get_object_or_404(Student, user=request.user)
    
    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('session', 'session__subject', 'session__tutor')
    
    return render(request, 'tutoring_sessions/session_list.html', {
        'enrollments': enrollments,
    })

@login_required
def cancel_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user.student)
    session=enrollment.session
    enrollment.delete()
    
    if session.enrolled_count > 0:
        session.enrolled_count -= 1
        session.save()
    messages.success(request, f'Successfully canceled enrollment from {session.class_code}.') # Added success message for clarity
    return redirect('students:sessions')

@login_required
def available_sessions(request):
    """Display available sessions that have space"""
    student = get_object_or_404(Student, user=request.user)
    
    # Get the IDs of sessions the student is already enrolled in
    enrolled_session_ids = Enrollment.objects.filter(
        student=student, 
        is_active=True
    ).values_list('session_id', flat=True)
    
    # Get sessions that are 'scheduled' and the student is not enrolled in
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
    """Enroll in a session"""
    if request.method != 'POST':
        return redirect('tutoring_sessions:available_sessions')
    
    student = get_object_or_404(Student, user=request.user)
    session = get_object_or_404(Session, id=session_id)
    
    # Check if session is full
    if session.enrolled_count >= session.capacity:
        messages.error(request, 'Session is full, cannot enroll!')
        return redirect('tutoring_sessions:available_sessions')
    
    # Check status
    if session.status != 'scheduled':
        messages.error(request, 'Only scheduled sessions can be enrolled in!')
        return redirect('tutoring_sessions:available_sessions')
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=student, session=session, is_active=True).exists():
        messages.warning(request, 'You are already enrolled in this session!')
        return redirect('tutoring_sessions:available_sessions')
    
    # Create enrollment
    Enrollment.objects.create(
        student=student,
        session=session,
        is_active=True
    )
    
    # Increment enrolled_count
    session.enrolled_count += 1
    session.save()
    
    messages.success(request, f'Successfully enrolled in {session.class_code}!')
    return redirect('students:sessions')

@login_required
def reschedule_session(request, enrollment_id):
    # Get current enrollment
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student__user=request.user)
    current_session = enrollment.session
    
    # Only allow rescheduling if the session is ongoing (Note: This logic might need review based on actual use case)
    if current_session.status != 'ongoing':
        messages.error(request, 'Only ongoing sessions can be rescheduled.')
        return redirect('students:sessions')
    
    # Get a list of other sessions with the same subject, same tutor, and not full
    available_sessions = Session.objects.filter(
        subject=current_session.subject,
        tutor=current_session.tutor,
        status__in=['scheduled', 'ongoing']
    ).exclude(
        id=current_session.id
    ).filter(
        enrolled_count__lt=F('capacity')
    ).select_related('subject', 'tutor').order_by('class_code') # Added select_related for better performance/display
    
    if request.method == 'POST':
        new_session_id = request.POST.get('new_session_id')
        new_session = get_object_or_404(Session, id=new_session_id)
        
        # Validation checks
        if new_session.subject != current_session.subject:
            messages.error(request, 'The new session must be the same subject.')
            return redirect('tutoring_sessions:reschedule_session', enrollment_id=enrollment_id)
        
        if new_session.tutor != current_session.tutor:
            messages.error(request, 'The new session must have the same tutor.')
            return redirect('tutoring_sessions:reschedule_session', enrollment_id=enrollment_id)
        
        if new_session.enrolled_count >= new_session.capacity:
            messages.error(request, 'The new session is full.')
            return redirect('tutoring_sessions:reschedule_session', enrollment_id=enrollment_id)
        
        # Check if the student is already enrolled in the new session
        if Enrollment.objects.filter(student=enrollment.student, session=new_session, is_active=True).exists():
            messages.error(request, 'You are already enrolled in this session.')
            return redirect('tutoring_sessions:reschedule_session', enrollment_id=enrollment_id)
        
        # Perform reschedule
        # Decrement enrolled_count of the old session
        current_session.enrolled_count -= 1
        current_session.save()
        
        # Update enrollment
        enrollment.session = new_session
        enrollment.save()
        
        # Increment enrolled_count of the new session
        new_session.enrolled_count += 1
        new_session.save()
        
        messages.success(request, f'Successfully rescheduled to class {new_session.class_code}!')
        return redirect('students:sessions')
    
    context = {
        'enrollment': enrollment,
        'current_session': current_session,
        'available_sessions': available_sessions,
    }
    return render(request, 'tutoring_sessions/reschedule.html', context)

@login_required
def tutor_reschedule_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, tutor__user=request.user)

    if session.status not in ['scheduled', 'ongoing']:
        messages.error(request, 'Cannot change the schedule for a completed or cancelled session.')
        return redirect('tutors:sessions')

    if request.method == 'POST':
        selected_value = request.POST.get('days')  # Only retrieve 1 selected checkbox value
        new_start_time = request.POST.get('start_time')
        new_end_time = request.POST.get('end_time')

        if not all([selected_value, new_start_time, new_end_time]):
            messages.error(request, 'Please fill in all required information.')
            return redirect('tutors:sessions')

        # Convert value (0, 1, 2...) to day name
        day_dict = dict(Session.DAY_CHOICES)
        session.days = day_dict.get(selected_value, selected_value)  # e.g., "Monday"
        session.start_time = new_start_time
        session.end_time = new_end_time
        session.save()

        messages.success(request, f'Successfully updated the schedule for class {session.class_code}!')
        return redirect('tutors:sessions')

    day_choices = Session.DAY_CHOICES
    # Get current value (day label) for default check
    current_day_label = session.days

    context = {
        'session': session,
        'day_choices': day_choices,
        'current_day_label': current_day_label,
    }
    return render(request, 'tutoring_sessions/tutor_reschedule.html', context)



@login_required
def tutor_cancel_session(request, session_id):
    """Tutor cancels a session"""
    # Check if user is a tutor
    if not hasattr(request.user, 'tutor'):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('home')
    
    # Get session and check ownership
    session = get_object_or_404(Session, id=session_id, tutor=request.user.tutor)
    
    # Only allow cancellation for scheduled or ongoing sessions
    if session.status not in ['scheduled', 'ongoing']:
        messages.error(request, f'Cannot cancel a class with status "{session.get_status_display()}".')
        return redirect('tutors:sessions')
    
    # Get list of active enrollments
    active_enrollments = Enrollment.objects.filter(session=session, is_active=True)
    student_count = active_enrollments.count()
    
    # Update session status
    session.status = 'cancelled'
    session.enrolled_count = 0  # Reset enrolled count
    session.save()
    
    # Deactivate all enrollments
    active_enrollments.update(is_active=False)
    
    # Success notification
    if student_count > 0:
        messages.success(request, f'Canceled class {session.class_code}. {student_count} students have been unenrolled.')
    else:
        messages.success(request, f'Canceled class {session.class_code}.')
    
    return redirect('tutors:sessions')

@login_required
def view_session_students(request, session_id):
    """View the list of students in a session"""
    # Check access permission
    if not hasattr(request.user, 'tutor'):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    session = get_object_or_404(Session, id=session_id, tutor=request.user.tutor)
    
    # Get list of enrollments
    enrollments = Enrollment.objects.filter(
        session=session,
        is_active=True
    ).select_related('student', 'student__user').order_by('student__full_name')
    
    # TODO: Add attendance_count if Attendance model exists
    # Default placeholder
    for enrollment in enrollments:
        enrollment.attendance_count = 0  # Calculated from Attendance model
    
    context = {
        'session': session,
        'enrollments': enrollments,
        'search_query': request.GET.get('search', ''),
    }
    return render(request, 'tutoring_sessions/view_students.html', context)