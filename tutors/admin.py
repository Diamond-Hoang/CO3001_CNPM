from django.contrib import admin
from .models import Tutor, TutorAvailability

# Inline để hiển thị TutorAvailability ngay trong form Tutor
class TutorAvailabilityInline(admin.TabularInline):
    model = TutorAvailability
    extra = 1  # Số dòng trống mặc định để thêm mới
    fields = ('weekday', 'start_time', 'end_time', 'status', 'subject')
    readonly_fields = ()  # Nếu muốn chỉ xem, có thể thêm tên field vào đây

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'tutor_id', 'phone', 'email', 'major')
    search_fields = ('full_name', 'tutor_id', 'email')
    inlines = [TutorAvailabilityInline]  # Hiển thị inline availability
    filter_horizontal = ('expertise',)  # Dễ chọn nhiều môn trong form

@admin.register(TutorAvailability)
class TutorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'weekday', 'start_time', 'end_time', 'status', 'subject')
    list_filter = ('weekday', 'status', 'subject')
    search_fields = ('tutor__full_name', 'subject__name')
