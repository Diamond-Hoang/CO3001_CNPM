from django.contrib import admin
from django.utils.html import format_html
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'student_id', 'phone', 'email', 'avatar_preview']
    search_fields = ['full_name', 'student_id', 'email']
    readonly_fields = ['avatar_preview']  # nếu muốn chỉ hiển thị, không cho edit trực tiếp trong form

    # Hàm hiển thị avatar
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 50px; height:50px; object-fit: cover; border-radius:50%;" />', obj.avatar.url)
        return "(No Avatar)"
    avatar_preview.short_description = 'Avatar'
