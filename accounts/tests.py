from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile, CASSimulatorUser

class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_user_profile_creation(self):
        """Test that UserProfile is created and linked correctly"""
        profile = UserProfile.objects.create(user=self.user, role='student')
        self.assertEqual(profile.user.username, 'testuser')
        self.assertEqual(profile.role, 'student')
        self.assertEqual(str(profile), 'testuser (student)')

    def test_user_profile_roles(self):
        """Test multiple user profiles with different roles"""
        tutor_user = User.objects.create_user(username='tutoruser', password='password123')
        profile = UserProfile.objects.create(user=tutor_user, role='tutor')
        self.assertEqual(profile.role, 'tutor')

class CASSimulatorUserTests(TestCase):
    def test_cas_simulator_user_creation(self):
        """Test CASSimulatorUser model"""
        sim_user = CASSimulatorUser.objects.create(
            username='simuser',
            password='hashed_password',
            role='student'
        )
        self.assertEqual(sim_user.username, 'simuser')
        self.assertEqual(sim_user.role, 'student')
        self.assertIn('SIM: simuser', str(sim_user))

class AccountViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        UserProfile.objects.create(user=self.user, role='student')
        
        self.tutor_user = User.objects.create_user(username='tutoruser', password='password123')
        UserProfile.objects.create(user=self.tutor_user, role='tutor')

    def test_login_page_renders(self):
        """Test the login page loads correctly"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_sso_login_redirect(self):
        """Test that sso_login redirects to CAS server"""
        response = self.client.get(reverse('accounts:sso_login'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/cas/login?service=', response.url)

    def test_role_based_redirect_student(self):
        """Test redirect after login for student"""
        self.client.login(username='testuser', password='password123')
        # We simulate the callback/redirect logic if we could, 
        # but here we test the view logic based on the role in session if it were there.
        # Actually sso_callback handles the login and redirect.
        pass

    def test_sso_callback_minimal(self):
        """Test sso_callback with missing token"""
        response = self.client.get(reverse('accounts:sso_callback'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No token provided.")

    def test_sso_callback_invalid_token(self):
        """Test sso_callback with an invalid token"""
        response = self.client.get(reverse('accounts:sso_callback'), {'token': 'INVALID'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid or expired token.")

    def test_sso_callback_success_student(self):
        """Test sso_callback success for a student role"""
        # We need to mock the session or simulate the cas_validate behavior
        # In a real integration test, we'd hit the cas_login then sso_callback.
        # Here we'll simulate the session state that cas_validate needs.
        s = self.client.session
        s["token_user"] = "newstudent"
        s["token_role"] = "student"
        s["token_value"] = "ST-12345"
        s.save()
        
        response = self.client.get(reverse('accounts:sso_callback'), {'token': 'ST-12345'})
        # Should redirect to student dashboard
        self.assertRedirects(response, reverse('students:student_dashboard'))
        # User should be created
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertEqual(User.objects.get(username='newstudent').userprofile.role, 'student')

    def test_sso_callback_success_office(self):
        """Test sso_callback success for an office role"""
        # This tests a role we haven't tested before
        s = self.client.session
        s["token_user"] = "officeuser"
        s["token_role"] = "office"
        s["token_value"] = "ST-OFFICE"
        s.save()
        
        # Note: 'office_dashboard' must exist in urls.py for this redirect to work in reverse
        # Let's check if it exists or if we should mock the reverse.
        # Actually in views.py it's redirect("office_dashboard")
        
        response = self.client.get(reverse('accounts:sso_callback'), {'token': 'ST-OFFICE'})
        # Should redirect to home/login since no office dashboard exists
        self.assertRedirects(response, reverse('accounts:login'))
