from django.contrib import admin
from .models import Subject, Tutor, Student, Session, Enrollment, SessionMaterial, Feedback

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone']
    search_fields = ['full_name']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['class_code', 'subject', 'tutor', 'days', 'start_time', 'status']
    list_filter = ['status', 'subject']
    search_fields = ['class_code']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'enrolled_at', 'is_active']
    list_filter = ['is_active']

admin.site.register(SessionMaterial)
admin.site.register(Feedback)