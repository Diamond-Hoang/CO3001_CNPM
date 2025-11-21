from django.db import models
# from django.contrib.auth.models import User
# from tutoring_sessions.models import Subject

# class Tutor(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     full_name = models.CharField(max_length=100)
#     phone = models.CharField(max_length=15, blank=True)
#     expertise = models.ManyToManyField(Subject, related_name='tutors')
   
#     def __str__(self):
#         return self.full_name