from django.contrib import admin
from .models import Subject, Tutor, Student, Session, Enrollment, SessionMaterial, AdvisingSession

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']

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

@admin.register(AdvisingSession)
class AdvisingSessionAdmin(admin.ModelAdmin):
    list_display = (
        'main_session', 'tutor', 'date',
        'start_time', 'end_time', 'is_active'
    )
    list_filter = ('is_active', 'date', 'tutor')
    search_fields = ('main_session__class_code', 'tutor__user__username')