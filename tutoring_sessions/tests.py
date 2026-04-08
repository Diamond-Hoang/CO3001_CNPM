from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from students.models import Student
from tutors.models import Tutor
from accounts.models import UserProfile
from .models import Subject, Session, Enrollment, AdvisingSession, SessionMaterial
from django.utils import timezone
import datetime

class TutoringSessionsTests(TestCase):
    def setUp(self):
        # Create user for Student and Tutor
        self.student_user = User.objects.create_user(username='student1', password='pass123')
        self.tutor_user = User.objects.create_user(username='tutor1', password='pass123')
        
        # Create UserProfiles
        UserProfile.objects.create(user=self.student_user, role='student')
        UserProfile.objects.create(user=self.tutor_user, role='tutor')
        
        # Create Student and Tutor
        self.student = Student.objects.create(
            user=self.student_user,
            full_name='Test Student',
            student_id='S12345'
        )
        self.tutor = Tutor.objects.create(
            user=self.tutor_user,
            full_name='Test Tutor',
            tutor_id='T12345'
        )
        
        # Create Subject
        self.subject = Subject.objects.create(name='Mathematics', code='MATH101')
        
        # Create Session
        self.session = Session.objects.create(
            class_code='C101',
            subject=self.subject,
            tutor=self.tutor,
            days='0-2-4',  # Mon, Wed, Fri
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 30),
            capacity=20
        )

    def test_subject_str(self):
        self.assertEqual(str(self.subject), 'MATH101 - Mathematics')

    def test_session_str(self):
        self.assertEqual(str(self.session), 'C101 - Mathematics')

    def test_session_get_days_display(self):
        self.assertEqual(self.session.get_days_display(), 'Monday, Wednesday, Friday')

    def test_session_capacity_display(self):
        self.assertEqual(self.session.capacity_display, '0/20')
        
        # Update enrolled count manually for testing the property
        self.session.enrolled_count = 5
        self.assertEqual(self.session.capacity_display, '5/20')

    def test_enrollment_creation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            session=self.session
        )
        self.assertEqual(str(enrollment), 'Test Student - C101')
        self.assertTrue(enrollment.is_active)

    def test_advising_session_is_today(self):
        # Session today
        today = timezone.now().date()
        advising_today = AdvisingSession.objects.create(
            main_session=self.session,
            tutor=self.tutor,
            date=today,
            start_time=datetime.time(14, 0),
            end_time=datetime.time(15, 0)
        )
        self.assertTrue(advising_today.is_today)
        
        # Session tomorrow
        tomorrow = today + datetime.timedelta(days=1)
        advising_tomorrow = AdvisingSession.objects.create(
            main_session=self.session,
            tutor=self.tutor,
            date=tomorrow,
            start_time=datetime.time(14, 0),
            end_time=datetime.time(15, 0)
        )
        self.assertFalse(advising_tomorrow.is_today)

    def test_session_material(self):
        # We won't test the file upload here, just the model creation
        material = SessionMaterial.objects.create(
            session=self.session,
            title='Note 1',
            file='test.pdf'
        )
        self.assertEqual(str(material), 'C101 - Note 1')

class TutoringSessionViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_user(username='student1', password='password123')
        self.tutor_user = User.objects.create_user(username='tutor1', password='password123')
        
        UserProfile.objects.create(user=self.student_user, role='student')
        UserProfile.objects.create(user=self.tutor_user, role='tutor')
        
        self.student = Student.objects.create(user=self.student_user, full_name='Test Student', student_id='S1')
        self.tutor = Tutor.objects.create(user=self.tutor_user, full_name='Test Tutor', tutor_id='T1')
        
        self.subject = Subject.objects.create(name='Math', code='M1')
        self.session = Session.objects.create(
            class_code='SM1', subject=self.subject, tutor=self.tutor,
            days='1', start_time=datetime.time(9,0), end_time=datetime.time(10,0),
            capacity=1  # Small capacity to test "full session"
        )
        
        self.client.login(username='student1', password='password123')

    def test_enroll_session_success(self):
        """Test successful enrollment in a session"""
        response = self.client.post(reverse('tutoring_sessions:enroll_session', args=[self.session.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(student=self.student, session=self.session).exists())
        
        # Verify count incremented
        self.session.refresh_from_db()
        self.assertEqual(self.session.enrolled_count, 1)

    def test_enroll_full_session(self):
        """Test enrollment failure when session is full"""
        self.session.enrolled_count = 1
        self.session.save()
        
        response = self.client.post(reverse('tutoring_sessions:enroll_session', args=[self.session.id]))
        self.assertEqual(response.status_code, 302)
        # Verify enrollment was NOT created for THIS student (who isn't enrolled yet)
        self.assertFalse(Enrollment.objects.filter(student=self.student, session=self.session).exists())

    def test_cancel_enrollment(self):
        """Test canceling an enrollment"""
        enrollment = Enrollment.objects.create(student=self.student, session=self.session)
        self.session.enrolled_count = 1
        self.session.save()
        
        response = self.client.post(reverse('tutoring_sessions:cancel_enrollment', args=[enrollment.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Enrollment.objects.filter(id=enrollment.id).exists())
        
        # Verify count decremented
        self.session.refresh_from_db()
        self.assertEqual(self.session.enrolled_count, 0)

    def test_view_students_access_control(self):
        """Test that ONLY the tutor of the session can view its students"""
        # Logged in as student currently, should redirect/error
        response = self.client.get(reverse('tutoring_sessions:view_students', args=[self.session.id]))
        self.assertEqual(response.status_code, 302) # Redirects to login/dashboard
        
        # Log in as tutor
        self.client.login(username='tutor1', password='password123')
        response = self.client.get(reverse('tutoring_sessions:view_students', args=[self.session.id]))
        self.assertEqual(response.status_code, 200)

    def test_available_sessions_search(self):
        """Test searching for available sessions"""
        # Update existing session code to be more unique
        self.session.class_code = 'SESSION-MATH-001'
        self.session.save()

        # Create another session to filter
        another_subject = Subject.objects.create(name='Physics', code='PHY101')
        phys_session = Session.objects.create(
            class_code='SESSION-PHYS-001', subject=another_subject, tutor=self.tutor,
            days='2', start_time=datetime.time(14,0), end_time=datetime.time(15,0),
            capacity=10, status='scheduled'
        )
        
        # Search for 'Math' (case-insensitive)
        response = self.client.get(reverse('tutoring_sessions:available_sessions'), {'search': 'Math'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SESSION-MATH-001')
        self.assertNotContains(response, 'SESSION-PHYS-001')
        # Functional check
        self.assertIn(self.session, response.context['sessions'])
        self.assertNotIn(phys_session, response.context['sessions'])
        
        # Search for 'PHYS'
        response = self.client.get(reverse('tutoring_sessions:available_sessions'), {'search': 'PHYS'})
        self.assertContains(response, 'SESSION-PHYS-001')
        self.assertNotContains(response, 'SESSION-MATH-001')
        # Functional check
        self.assertIn(phys_session, response.context['sessions'])
        self.assertNotIn(self.session, response.context['sessions'])

    def test_duplicate_enrollment_prevention(self):
        """Test that a student cannot enroll twice in the same session"""
        Enrollment.objects.create(student=self.student, session=self.session, is_active=True)
        self.session.enrolled_count = 1
        self.session.save()
        
        # Try to enroll again
        response = self.client.post(reverse('tutoring_sessions:enroll_session', args=[self.session.id]))
        self.assertEqual(response.status_code, 302)
        
        # Count should still be 1
        self.assertEqual(Enrollment.objects.filter(student=self.student, session=self.session).count(), 1)
