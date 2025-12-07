from django.db import models
from django.contrib.auth.models import User

class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    tutor_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    expertise = models.ManyToManyField('tutoring_sessions.Subject', related_name='tutors')
    email = models.EmailField(blank=True)
    major = models.CharField(max_length=100, blank=True)
    dob = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True) 

    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutors"

class TutorAvailability(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('unavailable', 'Unavailable'),
    ]
    
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='availabilities')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    subject = models.ForeignKey('tutoring_sessions.Subject', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['tutor', 'weekday', 'start_time']
        ordering = ['weekday', 'start_time']
    
    def __str__(self):
        return f"{self.tutor.full_name} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"   