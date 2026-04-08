from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from students.models import Student
from tutors.models import Tutor
from accounts.models import UserProfile
from tutoring_sessions.models import Subject, Session, Enrollment
from .models import Feedback, SessionRequest, TechnicalReport, StudentProgress
import datetime

class FeedbackTests(TestCase):
    def setUp(self):
        # Setup basic data
        self.user = User.objects.create_user(username='teststudent', password='password')
        self.tutor_user = User.objects.create_user(username='testtutor', password='password')
        
        # Create UserProfiles
        UserProfile.objects.create(user=self.user, role='student')
        UserProfile.objects.create(user=self.tutor_user, role='tutor')
        
        self.student = Student.objects.create(user=self.user, full_name='Test Student', student_id='S111')
        self.tutor = Tutor.objects.create(user=self.tutor_user, full_name='Test Tutor', tutor_id='T111')
        self.subject = Subject.objects.create(name='Physics', code='PHY101')
        self.session = Session.objects.create(
            class_code='P1', subject=self.subject, tutor=self.tutor,
            days='1', start_time=datetime.time(9,0), end_time=datetime.time(10,0)
        )
        self.enrollment = Enrollment.objects.create(student=self.student, session=self.session)

    def test_feedback_creation(self):
        feedback = Feedback.objects.create(enrollment=self.enrollment, rating=5, comment='Great!')
        self.assertEqual(str(feedback), 'Feedback from Test Student')

    def test_session_request_validation(self):
        # Valid request
        req = SessionRequest(
            student=self.student, subject='Math', delivery_mode='online',
            date=datetime.date.today(), start_time=datetime.time(10,0), end_time=datetime.time(11,0)
        )
        req.full_clean() # Should not raise
        
        # Invalid request (end time before start)
        req.start_time = datetime.time(11,0)
        req.end_time = datetime.time(10,0)
        with self.assertRaises(ValidationError):
            req.clean()

    def test_technical_report_status(self):
        report = TechnicalReport.objects.create(
            user=self.user, problem_description='Login failed'
        )
        self.assertFalse(report.is_resolved())
        self.assertEqual(report.status, 'pending')
        
        report.mark_as_resolved()
        self.assertTrue(report.is_resolved())
        self.assertEqual(report.status, 'resolved')
        self.assertIsNotNone(report.resolved_at)

    def test_student_progress(self):
        progress = StudentProgress.objects.create(
            enrollment=self.enrollment,
            student=self.student,
            session=self.session,
            tutor=self.tutor,
            attendance=5,
            topics_covered=3
        )
        self.assertEqual(str(progress), 'Test Student - P1')

class FeedbackViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_user(username='student_v', password='password123')
        self.tutor_user = User.objects.create_user(username='tutor_v', password='password123')
        
        UserProfile.objects.create(user=self.student_user, role='student')
        UserProfile.objects.create(user=self.tutor_user, role='tutor')
        
        self.student = Student.objects.create(user=self.student_user, full_name='Student V', student_id='SV1')
        self.tutor = Tutor.objects.create(user=self.tutor_user, full_name='Tutor V', tutor_id='TV1')
        
        self.subject = Subject.objects.create(name='Logic', code='L1')
        self.session = Session.objects.create(
            class_code='SL1', subject=self.subject, tutor=self.tutor,
            days='1', start_time=datetime.time(9,0), end_time=datetime.time(10,0),
            status='completed'
        )
        self.enrollment = Enrollment.objects.create(student=self.student, session=self.session)
        
        self.client.login(username='student_v', password='password123')

    def test_feedback_submission_success(self):
        """Test successful feedback submission for a completed session"""
        response = self.client.post(reverse('feedback:feedback', args=[self.enrollment.id]), {
            'rating': 5,
            'comment': 'Amazing session!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Feedback.objects.filter(enrollment=self.enrollment, rating=5).exists())

    def test_feedback_restricted_to_completed(self):
        """Test that feedback cannot be submitted for non-completed sessions"""
        self.session.status = 'scheduled'
        self.session.save()
        
        response = self.client.post(reverse('feedback:feedback', args=[self.enrollment.id]), {
            'rating': 4,
            'comment': 'Too soon'
        })
        self.assertEqual(response.status_code, 302)
        # Verify NO feedback was created
        self.assertFalse(Feedback.objects.filter(enrollment=self.enrollment).exists())

    def test_technical_report_submission(self):
        """Test technical report submission view"""
        response = self.client.post(reverse('feedback:technical_report'), {
            'problem_description': 'Buttons are not clickable on mobile',
            'priority': 'high'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TechnicalReport.objects.filter(user=self.student_user, priority='high').exists())

    def test_view_feedback_access_control(self):
        """Test that only the session tutor can view feedback"""
        # Enrollment and feedback
        Feedback.objects.create(enrollment=self.enrollment, rating=5, comment='Good')
        
        # Student tries to view feedback list
        response = self.client.get(reverse('feedback:view_feedback', args=[self.session.id]))
        # Note: In views.py, it uses get_object_or_404(Session, id=session_id, tutor=request.user.tutor)
        # Since student has no .tutor attribute, this might raise AttributeError or 404.
        self.assertEqual(response.status_code, 404) # Or 302/403 depending on implementation
        
        # Correct tutor views it
        self.client.login(username='tutor_v', password='password123')
        response = self.client.get(reverse('feedback:view_feedback', args=[self.session.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Good')

    def test_request_session_view(self):
        """Test the request session view for students"""
        # Testing a valid POST request
        response = self.client.post(reverse('feedback:request_session'), {
            'subject': 'Biology',
            'delivery_mode': 'online',
            'date': (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
            'start_time': '10:00',
            'end_time': '11:00'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SessionRequest.objects.filter(student=self.student, subject='Biology').exists())

    def test_request_session_past_date(self):
        """Test validation: cannot request a session in the past"""
        past_date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
        response = self.client.post(reverse('feedback:request_session'), {
            'subject': 'Biology',
            'delivery_mode': 'online',
            'date': past_date,
            'start_time': '10:00',
            'end_time': '11:00'
        })
        # Should stay on page with error
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SessionRequest.objects.filter(date=past_date).exists())

    def test_student_progress_logic(self):
        """Test StudentProgress model logic and constraints"""
        progress = StudentProgress.objects.create(
            enrollment=self.enrollment,
            student=self.student,
            session=self.session,
            tutor=self.tutor,
            attendance=4,
            topics_covered=2,
            comprehension_level=5
        )
        self.assertEqual(progress.comprehension_level, 5)
        self.assertEqual(str(progress), f"{self.student.full_name} - {self.session.class_code}")
