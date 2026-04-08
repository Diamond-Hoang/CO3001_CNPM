from django.contrib import admin

from .models import UserProfile, CASSimulatorUser

admin.site.register(UserProfile)

@admin.register(CASSimulatorUser)
class CASSimulatorUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'created_at')
    search_fields = ('username',)
    list_filter = ('role',)
