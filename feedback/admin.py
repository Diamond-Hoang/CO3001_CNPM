from django.contrib import admin
from .models import Feedback
from .models import SessionRequest, TechnicalReport, StudentProgress

# Register your models here.
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'rating', 'created_at']
    search_fields = ['enrollment__student__full_name', 'enrollment__session__subject']

@admin.register(SessionRequest)
class SessionRequestAdmin(admin.ModelAdmin):
    list_display = ['subject', 'student', 'delivery_mode', 'date', 'start_time', 'end_time', 'created_at']
    list_filter = [ 'delivery_mode', 'date']
    search_fields = ['subject', 'student__username']
    date_hierarchy = 'created_at'

@admin.register(TechnicalReport)
class TechnicalReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'priority', 'created_at', 'is_resolved']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['user__username', 'problem_description', 'admin_notes']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('user', 'problem_description', 'created_at')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'resolved_at')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_pending']
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} report(s) marked as resolved.')
    mark_as_resolved.short_description = "Mark selected reports as resolved"
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} report(s) marked as pending.')
    mark_as_pending.short_description = "Mark selected reports as pending"

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = [
        'student',
        'session',
        'tutor',
        'attendance',
        'topics_covered',
        'comprehension_level',
        'goals_achieved',
        'created_at'
    ]
    list_filter = ['tutor', 'session', 'created_at']
    search_fields = ['student__full_name', 'session__class_code', 'tutor__full_name']

    # 🔥 Remove enrollment, keep only these as autocomplete
    autocomplete_fields = ['student', 'session', 'tutor']