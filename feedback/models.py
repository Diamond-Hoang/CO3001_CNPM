from django.db import models
from students.models import Student  # Import Student từ app students
from tutoring_sessions.models import Enrollment
# Create your models here.
class Feedback(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback from {self.enrollment.student.full_name}"