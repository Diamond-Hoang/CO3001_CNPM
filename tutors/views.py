from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Tutor, TutorAvailability
from tutoring_sessions.models import Session, Enrollment, SessionMaterial, Subject, AdvisingSession
from .forms import AvatarUpdateForm, ExpertiseUpdateForm
from feedback.models import StudentProgress
from students.models import Student
from django.http import JsonResponse
from django.contrib import messages
from datetime import time, date, datetime, timedelta 
from django.utils import timezone

@login_required
def dashboard(request):
    """Dashboard cho tutor - hiển thị today sessions và upcoming advising sessions"""
    if not hasattr(request.user, 'tutor'):
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('home')
    
    tutor = request.user.tutor
    today = timezone.now().date()
    
    # Today's regular sessions (lọc theo ngày trong tuần)
    weekday_map = {
        0: '2',   # Monday
        1: '3',   # Tuesday
        2: '4',   # Wednesday
        3: '5',   # Thursday
        4: '6',   # Friday
        5: '7',   # Saturday
        6: 'cn',  # Sunday
    }
    today_weekday = weekday_map[today.weekday()]
    
    # Sessions hôm nay (sessions chính có ngày hôm nay trong days)
    today_sessions = Session.objects.filter(
        tutor=tutor,
        status__in=['scheduled', 'ongoing'],
        days__contains=today_weekday
    ).select_related('subject').order_by('start_time')
    
    # Upcoming advising sessions (từ hôm nay trở đi, trong 7 ngày tới)
    next_week = today + timedelta(days=7)
    upcoming_advising = AdvisingSession.objects.filter(
        tutor=tutor,
        date__gte=today,
        date__lte=next_week,
        is_active=True
    ).select_related('main_session', 'main_session__subject').order_by('date', 'start_time')
    
    # Session colors (để tạo màu sắc đa dạng)
    colors = ['blue', 'green', 'mint', 'pink', 'peach', 'purple', 'orange', 'teal']
    
    context = {
        'today_sessions': today_sessions,
        'upcoming_advising': upcoming_advising,
        'colors': colors,
        'today': today,
    }
    return render(request, 'tutors/dashboard.html', context)

@login_required
def profile(request):
    if request.user.userprofile.role != 'tutor':
        return render(request, '403.html', status=403)
    tutor = Tutor.objects.get(user=request.user)
    all_subjects = Subject.objects.all().order_by('name')
    
    context = {
        'tutor': tutor,
        'all_subjects': all_subjects,
    }
    return render(request, 'tutors/profile.html', context)

@login_required
def sessions(request):
    if request.user.userprofile.role != 'tutor':
        return render(request, '403.html', status=403)
    tutor = request.user.tutor  # Giả sử user có liên kết với Tutor
    sessions = Session.objects.filter(tutor=tutor).order_by('-created_at')
    return render(request, 'tutors/sessions.html', {'sessions': sessions})

@login_required
def session_materials(request, session_id):
    session = get_object_or_404(Session, id=session_id)

    # Chỉ tutor của session được upload
    if request.user != session.tutor.user:
        messages.error(request, "You do not have permission for this session.")
        return redirect('tutors:tutor_sessions')

    # Xử lý upload file mà không dùng ModelForm
    if request.method == "POST":
        title = request.POST.get("title")
        file = request.FILES.get("file")

        if not title or not file:
            messages.error(request, "Please provide title and file.")
        else:
            SessionMaterial.objects.create(
                session=session,
                title=title,
                file=file
            )
            messages.success(request, "Material added successfully.")
            return redirect('tutors:session_materials', session_id=session.id)

    materials = session.materials.all()

    return render(request, "tutors/session_material.html", {
        "session": session,
        "materials": materials
    })


@login_required
def update_avatar(request):
    if request.method == 'POST':
        tutor = request.user.tutor
        form = AvatarUpdateForm(request.POST, request.FILES, instance=tutor)
        
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'avatar_url': tutor.avatar.url if tutor.avatar else None
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def update_expertise(request):
    try:
        tutor = request.user.tutor
        expertise_ids = request.POST.getlist('expertise')
        
        # Clear current expertise and set new ones
        tutor.expertise.clear()
        if expertise_ids:
            subjects = Subject.objects.filter(id__in=expertise_ids)
            tutor.expertise.set(subjects)
        
        # Get updated expertise names
        expertise_names = [subject.name for subject in tutor.expertise.all()]
        expertise_str = ', '.join(expertise_names) if expertise_names else 'N/A'
        
        return JsonResponse({
            'success': True,
            'expertise': expertise_str
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def availability_schedule(request):
    """Display tutor's weekly schedule"""
    tutor = request.user.tutor
    
    # Get all availabilities for this tutor
    availabilities = TutorAvailability.objects.filter(tutor=tutor).select_related('subject')
    
    # Time slots (7:00 AM to 8:00 PM in 50-minute intervals)
    time_slots = []
    start_hour = 7
    end_hour = 21
    
    for hour in range(start_hour, end_hour):
        time_slots.append({
            'start': time(hour, 0),
            'end': time(hour, 50),
            'label': f"{hour:02d}h00-{hour:02d}h50"
        })
    
    # Organize availabilities by weekday and time
    schedule_data = {}
    for availability in availabilities:
        time_str = availability.start_time.strftime('%H:%M')  # ra "09:00"
        key = f"{availability.weekday}_{time_str}"
        schedule_data[key] = availability

    # Get all subjects for the form
    subjects = Subject.objects.all().order_by('name')
    
    context = {
        'tutor': tutor,
        'time_slots': time_slots,
        'schedule_data': schedule_data,
        'subjects': subjects,
        'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    }
    
    return render(request, 'tutors/availability.html', context)

@login_required
@require_POST
def set_availability(request):
    """Set or update tutor availability for a specific time slot"""
    try:
        tutor = request.user.tutor
        weekday = int(request.POST.get('weekday'))
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        subject_id = request.POST.get('subject_id')
        status = request.POST.get('status', 'available')
        
        # Get or create availability
        availability, created = TutorAvailability.objects.get_or_create(
            tutor=tutor,
            weekday=weekday,
            start_time=start_time,
            defaults={
                'end_time': end_time,
                'status': status,
                'subject_id': subject_id if subject_id else None
            }
        )
        
        if not created:
            # Update existing availability
            availability.end_time = end_time
            availability.status = status
            availability.subject_id = subject_id if subject_id else None
            availability.save()
        
        subject_name = availability.subject.name if availability.subject else None
        
        return JsonResponse({
            'success': True,
            'message': 'Availability updated successfully',
            'subject_name': subject_name,
            'status': availability.status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_POST
def delete_availability(request):
    """Delete a specific availability slot"""
    try:
        tutor = request.user.tutor
        availability_id = request.POST.get('availability_id')
        
        availability = TutorAvailability.objects.get(
            id=availability_id,
            tutor=tutor
        )
        availability.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Availability deleted successfully'
        })
        
    except TutorAvailability.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Availability not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def availability_schedule_debug(request):
    tutor = request.user.tutor
    availabilities = TutorAvailability.objects.filter(tutor=tutor)
    time_slots = [{"start": str(time(h,0)), "end": str(time(h,50))} for h in range(7,21)]
    schedule_data = {f"{a.weekday}_{a.start_time}": str(a) for a in availabilities}
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    return JsonResponse({
        "time_slots": time_slots,
        "schedule_data": schedule_data,
        "weekdays": weekdays,
        "availabilities_count": availabilities.count()
    })

@login_required
def student_progress(request, student_id, session_id):
    """Xem và cập nhật progress của student"""
    # Kiểm tra quyền truy cập
    if request.user.userprofile.role != 'tutor':
        return render(request, '403.html', status=403)
    
    tutor = request.user.tutor
    student = get_object_or_404(Student, id=student_id)
    session = get_object_or_404(Session, id=session_id, tutor=tutor)
    enrollment = get_object_or_404(Enrollment, student=student, session=session, is_active=True)
    
    # Lấy hoặc tạo progress record
    progress, created = StudentProgress.objects.get_or_create(
        student=student,
        session=session,
        defaults={
            'enrollment': enrollment,
            'tutor': tutor,
            'attendance': 0,
            'topics_covered': 0,
            'comprehension_level': 0,
            'goals_achieved': 0,
        }
    )
    
    if request.method == 'POST':
        # Cập nhật progress
        progress.attendance = int(request.POST.get('attendance', 0))
        progress.topics_covered = int(request.POST.get('topics_covered', 0))
        progress.comprehension_level = int(request.POST.get('comprehension_level', 0))
        progress.goals_achieved = int(request.POST.get('goals_achieved', 0))
        progress.area_for_improvement = request.POST.get('area_for_improvement', '')
        progress.notes = request.POST.get('notes', '')
        progress.save()
        messages.success(request, f'Đã cập nhật progress cho {student.full_name}!')
        return redirect('tutors/sessions.html', session_id=session.id)
    
    context = {
        'student': student,
        'session': session,
        'progress': progress,
        'tutor': tutor,
    }
    return render(request, 'tutors/student_progress.html', context)

@login_required
def create_advising_session(request):
    """Tutor tạo advising session (lớp phụ đạo) từ session chính"""
    if not hasattr(request.user, 'tutor'):
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('home')
    
    tutor = request.user.tutor
    
    # Lấy các sessions mà tutor đang dạy
    tutor_sessions = Session.objects.filter(
        tutor=tutor,
        status__in=['scheduled', 'ongoing']
    ).select_related('subject')
    
    if request.method == 'POST':
        main_session_id = request.POST.get('main_session')
        advising_date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        location = request.POST.get('location', '')
        notes = request.POST.get('notes', '')
        
        # Validate
        if not all([main_session_id, advising_date, start_time, end_time]):
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
            return redirect('tutors:create_advising_session')
        
        # Kiểm tra ngày phải từ hôm nay trở đi
        advising_date_obj = datetime.strptime(advising_date, '%Y-%m-%d').date()
        if advising_date_obj < date.today():
            messages.error(request, 'Không thể tạo lớp phụ đạo cho ngày trong quá khứ.')
            return redirect('tutors:create_advising_session')
        
        main_session = get_object_or_404(Session, id=main_session_id, tutor=tutor)
        
        # Tạo advising session
        AdvisingSession.objects.create(
            main_session=main_session,
            tutor=tutor,
            date=advising_date_obj,
            start_time=start_time,
            end_time=end_time,
            location=location,
            notes=notes,
        )
        
        messages.success(request, f'Đã tạo lớp phụ đạo cho {main_session.class_code} vào ngày {advising_date}!')
        return redirect('tutors:sessions')
    
    context = {
        'tutor_sessions': tutor_sessions,
    }
    return render(request, 'tutors/create_advising_session.html', context)

@login_required
def tutor_dashboard(request):
    """Dashboard cho tutor - hiển thị today sessions và upcoming advising sessions"""
    if not hasattr(request.user, 'tutor'):
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('home')
    
    tutor = request.user.tutor
    today = timezone.now().date()
    
    # Today's regular sessions (lọc theo ngày trong tuần)
    weekday_map = {
        0: 'cn',  # Sunday
        1: '2',   # Monday
        2: '3',   # Tuesday
        3: '4',   # Wednesday
        4: '5',   # Thursday
        5: '6',   # Friday
        6: '7',   # Saturday
    }
    today_weekday = weekday_map[today.weekday()]
    
    # Sessions hôm nay (sessions chính có ngày hôm nay trong days)
    today_sessions = Session.objects.filter(
        tutor=tutor,
        status__in=['scheduled', 'ongoing'],
        days__contains=today_weekday
    ).select_related('subject').order_by('start_time')
    
    # Upcoming advising sessions (từ hôm nay trở đi, trong 7 ngày tới)
    next_week = today + timedelta(days=7)
    upcoming_advising = AdvisingSession.objects.filter(
        tutor=tutor,
        date__gte=today,
        date__lte=next_week,
        is_active=True
    ).select_related('main_session', 'main_session__subject').order_by('date', 'start_time')
    
    # Session colors (để tạo màu sắc đa dạng)
    colors = ['blue', 'green', 'mint', 'pink', 'peach', 'purple', 'orange', 'teal']
    
    context = {
        'today_sessions': today_sessions,
        'upcoming_advising': upcoming_advising,
        'colors': colors,
        'today': today,
    }
    return render(request, 'tutors/dashboard.html', context)