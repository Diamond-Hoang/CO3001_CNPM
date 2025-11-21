from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True, default='')
    
    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"