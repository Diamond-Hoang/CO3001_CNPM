from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
        ('admin', 'Admin'),
        ('office', 'Office'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
class CASSimulatorUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) # To store hashed password
    role = models.CharField(max_length=20, choices=UserProfile.ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SIM: {self.username} ({self.role})"

    class Meta:
        verbose_name = "CAS Simulation User"
        verbose_name_plural = "CAS Simulation Users"
