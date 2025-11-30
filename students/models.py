from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    major = models.CharField(max_length=100, blank=True)
    dob = models.DateField(null=True, blank=True)
    sp_needs = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # Thêm trường avatar

    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"