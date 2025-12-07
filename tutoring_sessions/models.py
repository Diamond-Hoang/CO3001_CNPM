from django.db import models
from django.contrib.auth.models import User
from students.models import Student  # Import Student từ app students
from tutors.models import Tutor

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Session(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    DAY_CHOICES = [
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ]
    
    class_code = models.CharField(max_length=20)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    days = models.CharField(max_length=50)  # Ví dụ: "2-3-4"
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.IntegerField(default=30)
    enrolled_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.class_code} - {self.subject.name}"
    
    def get_days_display(self):
        mapping = dict(self.DAY_CHOICES)
        return ", ".join(mapping[d] for d in self.days.split("-"))
    
    @property
    def capacity_display(self):
        return f"{self.enrolled_count}/{self.capacity}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'session')
    
    def __str__(self):
        return f"{self.student.full_name} - {self.session.class_code}"

class SessionMaterial(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='session_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.session.class_code} - {self.title}"
    
class AdvisingSession(models.Model):
    """Lớp phụ đạo thêm dựa trên session chính"""
    main_session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='advising_sessions')
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    date = models.DateField()  # Ngày cụ thể
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-start_time']
    
    def __str__(self):
        return f"Advising: {self.main_session.class_code} - {self.date}"
    
    @property
    def is_today(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.date == today
    
