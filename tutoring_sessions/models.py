from django.db import models
from django.contrib.auth.models import User
from students.models import Student  # Import Student từ app students

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    expertise = models.ManyToManyField(Subject, related_name='tutors')
    
    def __str__(self):
        return self.full_name

class Session(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    DAY_CHOICES = [
        ('2', 'Thứ 2'),
        ('3', 'Thứ 3'),
        ('4', 'Thứ 4'),
        ('5', 'Thứ 5'),
        ('6', 'Thứ 6'),
        ('7', 'Thứ 7'),
        ('cn', 'Chủ nhật'),
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

class Feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.enrollment.student.full_name}"