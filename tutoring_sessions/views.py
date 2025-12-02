from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F
from .models import Session, Enrollment, SessionMaterial
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

@login_required
def reschedule_session(request, enrollment_id):
    # Lấy enrollment hiện tại
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, student__user=request.user)
    current_session = enrollment.session
    
    # Chỉ cho phép reschedule nếu session đang ongoing
    if current_session.status != 'ongoing':
        messages.error(request, 'Chỉ có thể reschedule các session đang diễn ra.')
        return redirect('students:sessions')
    
    # Lấy danh sách các session khác cùng môn, cùng tutor, chưa đầy
    available_sessions = Session.objects.filter(
        subject=current_session.subject,
        tutor=current_session.tutor,
        status__in=['scheduled', 'ongoing']
    ).exclude(
        id=current_session.id
    ).filter(
        enrolled_count__lt=F('capacity')
    )
    
    if request.method == 'POST':
        new_session_id = request.POST.get('new_session_id')
        new_session = get_object_or_404(Session, id=new_session_id)
        
        # Kiểm tra điều kiện
        if new_session.subject != current_session.subject:
            messages.error(request, 'Session mới phải cùng môn học.')
            return redirect('tutoring_sessions:reschedule_session', enrollment_id=enrollment_id)
        
        if new_session.tutor != current_session.tutor:
            messages.error(request, 'Session mới phải cùng giảng viên.')
            return redirect('tutoring_sessions:reschedule_session', enrollment_id=enrollment_id)
        
        if new_session.enrolled_count >= new_session.capacity:
            messages.error(request, 'Session mới đã đầy.')
            return redirect('tutoring_sessions:reschedule_session', enrollment_id=enrollment_id)
        
        # Kiểm tra xem student đã đăng ký session mới chưa
        if Enrollment.objects.filter(student=enrollment.student, session=new_session, is_active=True).exists():
            messages.error(request, 'Bạn đã đăng ký session này rồi.')
            return redirect('tutoring_sessions:reschedule_session', enrollment_id=enrollment_id)
        
        # Thực hiện reschedule
        # Giảm enrolled_count của session cũ
        current_session.enrolled_count -= 1
        current_session.save()
        
        # Cập nhật enrollment
        enrollment.session = new_session
        enrollment.save()
        
        # Tăng enrolled_count của session mới
        new_session.enrolled_count += 1
        new_session.save()
        
        messages.success(request, f'Đã chuyển sang lớp {new_session.class_code} thành công!')
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
        messages.error(request, 'Không thể thay đổi lịch của session đã hoàn thành hoặc đã hủy.')
        return redirect('tutors:sessions')

    if request.method == 'POST':
        selected_value = request.POST.get('days')  # chỉ lấy 1 checkbox được chọn
        new_start_time = request.POST.get('start_time')
        new_end_time = request.POST.get('end_time')

        if not all([selected_value, new_start_time, new_end_time]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
            return redirect('tutors:sessions')

        # Chuyển giá trị (0,1,2...) thành tên ngày
        day_dict = dict(Session.DAY_CHOICES)
        session.days = day_dict.get(selected_value, selected_value)  # ví dụ "Monday"
        session.start_time = new_start_time
        session.end_time = new_end_time
        session.save()

        messages.success(request, f'Đã cập nhật lịch học cho lớp {session.class_code}!')
        return redirect('tutors:sessions')

    day_choices = Session.DAY_CHOICES
    # Lấy giá trị hiện tại (tên ngày) để check mặc định
    current_day_label = session.days

    context = {
        'session': session,
        'day_choices': day_choices,
        'current_day_label': current_day_label,
    }
    return render(request, 'tutoring_sessions/tutor_reschedule.html', context)



@login_required
def tutor_cancel_session(request, session_id):
    """Tutor hủy session"""
    # Kiểm tra user có phải tutor không
    if not hasattr(request.user, 'tutor'):
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('home')
    
    # Lấy session và kiểm tra quyền sở hữu
    session = get_object_or_404(Session, id=session_id, tutor=request.user.tutor)
    
    # Chỉ cho phép hủy session scheduled hoặc ongoing
    if session.status not in ['scheduled', 'ongoing']:
        messages.error(request, f'Không thể hủy lớp có trạng thái "{session.get_status_display()}".')
        return redirect('tutors:sessions')
    
    # Lấy danh sách enrollments đang active
    active_enrollments = Enrollment.objects.filter(session=session, is_active=True)
    student_count = active_enrollments.count()
    
    # Cập nhật status của session
    session.status = 'cancelled'
    session.enrolled_count = 0  # Reset enrolled count
    session.save()
    
    # Deactivate tất cả enrollments
    active_enrollments.update(is_active=False)
    
    # Thông báo thành công
    if student_count > 0:
        messages.success(request, f'Đã hủy lớp {session.class_code}. {student_count} học sinh đã bị hủy đăng ký.')
    else:
        messages.success(request, f'Đã hủy lớp {session.class_code}.')
    
    return redirect('tutors:sessions')

@login_required
def view_session_students(request, session_id):
    """Xem danh sách students trong session"""
    # Kiểm tra quyền truy cập
    if not hasattr(request.user, 'tutor'):
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('home')
    
    session = get_object_or_404(Session, id=session_id, tutor=request.user.tutor)
    
    # Lấy danh sách enrollments
    enrollments = Enrollment.objects.filter(
        session=session,
        is_active=True
    ).select_related('student', 'student__user').order_by('student__full_name')
    
    # TODO: Thêm attendance_count nếu có model Attendance
    # Tạm thời để mặc định
    for enrollment in enrollments:
        enrollment.attendance_count = 0  # Tính từ Attendance model
    
    context = {
        'session': session,
        'enrollments': enrollments,
        'search_query': request.GET.get('search', ''),
    }
    return render(request, 'tutoring_sessions/view_students.html', context)