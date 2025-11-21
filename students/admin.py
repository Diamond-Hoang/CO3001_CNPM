from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'student_id', 'phone', 'email']
    search_fields = ['full_name', 'student_id', 'email']