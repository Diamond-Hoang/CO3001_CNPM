from django.db import models
from tutoring_sessions.models import Enrollment
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from students.models import Student

# Create your models here.
class Feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.enrollment.student.full_name}"
    
class SessionRequest(models.Model):
    DELIVERY_MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('hybrid', 'Hybrid'),
    ]
    
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='session_requests')
    subject = models.CharField(max_length=200)
    delivery_mode = models.CharField(max_length=10, choices=DELIVERY_MODE_CHOICES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Session Request'
        verbose_name_plural = 'Session Requests'
    
    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError('End time must be after start time')
    
    def __str__(self):
        return f"{self.subject} - {self.student.full_name} - {self.date}"
    
class TechnicalReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='technical_reports',
        help_text="User who reported the issue"
    )
    problem_description = models.TextField(
        max_length=150,
        help_text="Description of the technical problem (max 150 characters)"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Admin notes
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes from admin/support team"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Technical Report'
        verbose_name_plural = 'Technical Reports'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Report #{self.id} - {self.user.username} - {self.status}"
    
    def is_resolved(self):
        """Check if report is resolved"""
        return self.status == 'resolved'
    
    def mark_as_resolved(self):
        """Mark report as resolved"""
        from django.utils import timezone
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save()

# tutoring_sessions/models.py hoặc feedback/models.py

class StudentProgress(models.Model):
    enrollment = models.ForeignKey('tutoring_sessions.Enrollment', on_delete=models.CASCADE, related_name='progress_records')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    session = models.ForeignKey('tutoring_sessions.Session', on_delete=models.CASCADE)
    tutor = models.ForeignKey('tutors.Tutor', on_delete=models.CASCADE)
    
    # Progress metrics (out of 5)
    attendance = models.IntegerField(default=0)  # Số buổi đã tham gia
    topics_covered = models.IntegerField(default=0)  # Chủ đề đã học
    comprehension_level = models.IntegerField(default=0)  # Mức độ hiểu bài
    goals_achieved = models.IntegerField(default=0)  # Mục tiêu đạt được
    
    # Text fields
    area_for_improvement = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'session')
    
    def __str__(self):
        return f"{self.student.full_name} - {self.session.class_code}"