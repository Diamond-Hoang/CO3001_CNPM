# tutoring_sessions/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time
from students.models import Student
from tutors.models import Tutor
from .models import Subject, Session, Enrollment

class RescheduleSessionTestCase(TestCase):
    """Test cases cho chức năng reschedule session"""
    
    def setUp(self):
        """Khởi tạo dữ liệu test"""
        # Tạo user và student
        self.user = User.objects.create_user(
            username='student1',
            password='testpass123',
            email='student1@test.com'
        )
        self.student = Student.objects.create(
            user=self.user,
            full_name='Test Student',
            student_id='ST001'
        )
        
        # Tạo tutor
        self.tutor_user = User.objects.create_user(
            username='tutor1',
            password='tutorpass123',
            email='tutor1@test.com'
        )
        self.tutor = Tutor.objects.create(
            user=self.tutor_user,
            full_name='Test Tutor',
            employee_id='TU001'
        )
        
        # Tạo tutor khác
        self.tutor2_user = User.objects.create_user(
            username='tutor2',
            password='tutorpass123',
            email='tutor2@test.com'
        )
        self.tutor2 = Tutor.objects.create(
            user=self.tutor2_user,
            full_name='Test Tutor 2',
            employee_id='TU002'
        )
        
        # Tạo subject
        self.subject_math = Subject.objects.create(
            name='Mathematics',
            code='MATH101'
        )
        self.subject_physics = Subject.objects.create(
            name='Physics',
            code='PHY101'
        )
        
        # Tạo session hiện tại (ongoing)
        self.current_session = Session.objects.create(
            class_code='MATH101-A',
            subject=self.subject_math,
            tutor=self.tutor,
            days='2-4',
            start_time=time(9, 0),
            end_time=time(11, 0),
            capacity=30,
            enrolled_count=10,
            status='ongoing'
        )
        
        # Tạo enrollment cho student
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            session=self.current_session,
            is_active=True
        )
        
        # Tạo session mới cùng môn, cùng tutor (available)
        self.available_session = Session.objects.create(
            class_code='MATH101-B',
            subject=self.subject_math,
            tutor=self.tutor,
            days='3-5',
            start_time=time(13, 0),
            end_time=time(15, 0),
            capacity=30,
            enrolled_count=15,
            status='ongoing'
        )
        
        # Tạo session đã đầy
        self.full_session = Session.objects.create(
            class_code='MATH101-C',
            subject=self.subject_math,
            tutor=self.tutor,
            days='2-4-6',
            start_time=time(15, 0),
            end_time=time(17, 0),
            capacity=30,
            enrolled_count=30,
            status='ongoing'
        )
        
        # Tạo session khác môn học
        self.different_subject_session = Session.objects.create(
            class_code='PHY101-A',
            subject=self.subject_physics,
            tutor=self.tutor,
            days='2-4',
            start_time=time(9, 0),
            end_time=time(11, 0),
            capacity=30,
            enrolled_count=10,
            status='ongoing'
        )
        
        # Tạo session khác tutor
        self.different_tutor_session = Session.objects.create(
            class_code='MATH101-D',
            subject=self.subject_math,
            tutor=self.tutor2,
            days='2-4',
            start_time=time(9, 0),
            end_time=time(11, 0),
            capacity=30,
            enrolled_count=10,
            status='ongoing'
        )
        
        # Tạo session completed
        self.completed_session = Session.objects.create(
            class_code='MATH101-E',
            subject=self.subject_math,
            tutor=self.tutor,
            days='2-4',
            start_time=time(9, 0),
            end_time=time(11, 0),
            capacity=30,
            enrolled_count=10,
            status='completed'
        )
        
        self.client = Client()
    
    def test_reschedule_page_requires_login(self):
        """Test: Trang reschedule yêu cầu đăng nhập"""
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login'))
    
    def test_reschedule_page_loads_successfully(self):
        """Test: Trang reschedule load thành công khi đã đăng nhập"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MATH101-A')
        self.assertContains(response, 'Test Tutor')
    
    def test_available_sessions_displayed(self):
        """Test: Hiển thị các session available (cùng môn, cùng tutor, còn chỗ)"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        response = self.client.get(url)
        
        # Phải hiển thị session available
        self.assertContains(response, 'MATH101-B')
        
        # Không hiển thị session đã đầy
        self.assertNotContains(response, 'MATH101-C')
        
        # Không hiển thị session khác môn
        self.assertNotContains(response, 'PHY101-A')
        
        # Không hiển thị session khác tutor
        self.assertNotContains(response, 'MATH101-D')
        
        # Không hiển thị session hiện tại
        # (MATH101-A sẽ xuất hiện ở phần "Lớp hiện tại" nhưng không ở phần chọn)
    
    def test_reschedule_success(self):
        """Test: Reschedule thành công"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        
        # Lưu giá trị ban đầu
        old_enrolled_count = self.current_session.enrolled_count
        new_enrolled_count = self.available_session.enrolled_count
        
        # Thực hiện reschedule
        response = self.client.post(url, {
            'new_session_id': self.available_session.id
        })
        
        # Kiểm tra redirect
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('students:sessions'))
        
        # Refresh từ database
        self.enrollment.refresh_from_db()
        self.current_session.refresh_from_db()
        self.available_session.refresh_from_db()
        
        # Kiểm tra enrollment đã được cập nhật
        self.assertEqual(self.enrollment.session.id, self.available_session.id)
        
        # Kiểm tra enrolled_count đã được cập nhật
        self.assertEqual(self.current_session.enrolled_count, old_enrolled_count - 1)
        self.assertEqual(self.available_session.enrolled_count, new_enrolled_count + 1)
    
    def test_cannot_reschedule_to_full_session(self):
        """Test: Không thể reschedule sang session đã đầy"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        
        response = self.client.post(url, {
            'new_session_id': self.full_session.id
        })
        
        # Kiểm tra vẫn ở trang reschedule và có thông báo lỗi
        self.assertEqual(response.status_code, 302)
        
        # Refresh enrollment
        self.enrollment.refresh_from_db()
        
        # Kiểm tra enrollment không thay đổi
        self.assertEqual(self.enrollment.session.id, self.current_session.id)
    
    def test_cannot_reschedule_to_different_subject(self):
        """Test: Không thể reschedule sang session khác môn"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        
        response = self.client.post(url, {
            'new_session_id': self.different_subject_session.id
        })
        
        # Kiểm tra redirect với lỗi
        self.assertEqual(response.status_code, 302)
        
        # Refresh enrollment
        self.enrollment.refresh_from_db()
        
        # Kiểm tra enrollment không thay đổi
        self.assertEqual(self.enrollment.session.id, self.current_session.id)
    
    def test_cannot_reschedule_to_different_tutor(self):
        """Test: Không thể reschedule sang session khác tutor"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        
        response = self.client.post(url, {
            'new_session_id': self.different_tutor_session.id
        })
        
        # Kiểm tra redirect với lỗi
        self.assertEqual(response.status_code, 302)
        
        # Refresh enrollment
        self.enrollment.refresh_from_db()
        
        # Kiểm tra enrollment không thay đổi
        self.assertEqual(self.enrollment.session.id, self.current_session.id)
    
    def test_cannot_reschedule_already_enrolled_session(self):
        """Test: Không thể reschedule sang session đã đăng ký"""
        # Tạo enrollment cho available_session
        Enrollment.objects.create(
            student=self.student,
            session=self.available_session,
            is_active=True
        )
        
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        
        response = self.client.post(url, {
            'new_session_id': self.available_session.id
        })
        
        # Kiểm tra redirect với lỗi
        self.assertEqual(response.status_code, 302)
        
        # Kiểm tra enrollment gốc không thay đổi
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.session.id, self.current_session.id)
    
    def test_cannot_reschedule_completed_session(self):
        """Test: Không thể reschedule session đã completed"""
        # Tạo enrollment cho completed session
        completed_enrollment = Enrollment.objects.create(
            student=self.student,
            session=self.completed_session,
            is_active=True
        )
        
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[completed_enrollment.id])
        
        response = self.client.get(url)
        
        # Kiểm tra redirect về trang sessions với thông báo lỗi
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('students:sessions'))
    
    def test_cannot_reschedule_other_student_enrollment(self):
        """Test: Không thể reschedule enrollment của student khác"""
        # Tạo student khác
        other_user = User.objects.create_user(
            username='student2',
            password='testpass123'
        )
        other_student = Student.objects.create(
            user=other_user,
            full_name='Other Student',
            student_id='ST002'
        )
        
        # Tạo enrollment cho student khác
        other_enrollment = Enrollment.objects.create(
            student=other_student,
            session=self.current_session,
            is_active=True
        )
        
        # Login với student1
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[other_enrollment.id])
        
        response = self.client.get(url)
        
        # Kiểm tra trả về 404
        self.assertEqual(response.status_code, 404)
    
    def test_no_available_sessions_message(self):
        """Test: Hiển thị thông báo khi không có session nào available"""
        # Xóa tất cả các session khác
        Session.objects.exclude(id=self.current_session.id).delete()
        
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Không có lớp nào khác phù hợp để chuyển')
    
    def test_reschedule_updates_enrolled_count_correctly(self):
        """Test: Reschedule cập nhật enrolled_count chính xác"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        
        # Lưu giá trị ban đầu
        old_count = self.current_session.enrolled_count
        new_count = self.available_session.enrolled_count
        
        # Thực hiện reschedule
        self.client.post(url, {
            'new_session_id': self.available_session.id
        })
        
        # Refresh
        self.current_session.refresh_from_db()
        self.available_session.refresh_from_db()
        
        # Kiểm tra enrolled_count
        self.assertEqual(self.current_session.enrolled_count, old_count - 1)
        self.assertEqual(self.available_session.enrolled_count, new_count + 1)
    
    def test_multiple_reschedules(self):
        """Test: Có thể reschedule nhiều lần"""
        self.client.login(username='student1', password='testpass123')
        
        # Tạo session thứ 3
        third_session = Session.objects.create(
            class_code='MATH101-F',
            subject=self.subject_math,
            tutor=self.tutor,
            days='3-5-7',
            start_time=time(14, 0),
            end_time=time(16, 0),
            capacity=30,
            enrolled_count=5,
            status='ongoing'
        )
        
        # Reschedule lần 1: current -> available
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        self.client.post(url, {'new_session_id': self.available_session.id})
        
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.session.id, self.available_session.id)
        
        # Reschedule lần 2: available -> third
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        self.client.post(url, {'new_session_id': third_session.id})
        
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.session.id, third_session.id)
    
    def test_reschedule_with_invalid_session_id(self):
        """Test: Reschedule với session_id không tồn tại"""
        self.client.login(username='student1', password='testpass123')
        url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        
        response = self.client.post(url, {
            'new_session_id': 99999  # ID không tồn tại
        })
        
        # Kiểm tra trả về 404
        self.assertEqual(response.status_code, 404)
        
        # Kiểm tra enrollment không thay đổi
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.session.id, self.current_session.id)


class RescheduleIntegrationTestCase(TestCase):
    """Integration tests cho toàn bộ flow reschedule"""
    
    def setUp(self):
        """Khởi tạo dữ liệu test"""
        self.user = User.objects.create_user(
            username='student1',
            password='testpass123'
        )
        self.student = Student.objects.create(
            user=self.user,
            full_name='Test Student',
            student_id='ST001'
        )
        
        self.tutor_user = User.objects.create_user(
            username='tutor1',
            password='tutorpass123'
        )
        self.tutor = Tutor.objects.create(
            user=self.tutor_user,
            full_name='Test Tutor',
            employee_id='TU001'
        )
        
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH101'
        )
        
        self.session1 = Session.objects.create(
            class_code='MATH101-A',
            subject=self.subject,
            tutor=self.tutor,
            days='2-4',
            start_time=time(9, 0),
            end_time=time(11, 0),
            capacity=30,
            enrolled_count=1,
            status='ongoing'
        )
        
        self.session2 = Session.objects.create(
            class_code='MATH101-B',
            subject=self.subject,
            tutor=self.tutor,
            days='3-5',
            start_time=time(13, 0),
            end_time=time(15, 0),
            capacity=30,
            enrolled_count=0,
            status='ongoing'
        )
        
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            session=self.session1,
            is_active=True
        )
        
        self.client = Client()
    
    def test_full_reschedule_workflow(self):
        """Test: Toàn bộ workflow từ sessions page -> reschedule -> back to sessions"""
        self.client.login(username='student1', password='testpass123')
        
        # 1. Truy cập trang sessions
        sessions_url = reverse('students:sessions')
        response = self.client.get(sessions_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MATH101-A')
        
        # 2. Click vào reschedule icon
        reschedule_url = reverse('tutoring_sessions:reschedule_session', args=[self.enrollment.id])
        response = self.client.get(reschedule_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MATH101-B')
        
        # 3. Chọn session mới và submit
        response = self.client.post(reschedule_url, {
            'new_session_id': self.session2.id
        })
        self.assertEqual(response.status_code, 302)
        
        # 4. Quay lại trang sessions và kiểm tra
        response = self.client.get(sessions_url)
        self.assertContains(response, 'MATH101-B')
        self.assertNotContains(response, 'MATH101-A')
        
        # 5. Kiểm tra dữ liệu trong database
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.session.class_code, 'MATH101-B')
        
        self.session1.refresh_from_db()
        self.assertEqual(self.session1.enrolled_count, 0)
        
        self.session2.refresh_from_db()
        self.assertEqual(self.session2.enrolled_count, 1)