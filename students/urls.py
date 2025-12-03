from django.urls import path
from . import views
from library import views as library_views
from feedback import views as feedback_views
from tutoring_sessions import views as tutoring_views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard, name='student_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('sessions/', views.sessions, name='sessions'),
    path('sessions/material/<int:session_id>/', views.session_material, name='session_material'),  # ← THÊM session_id
    path('find_sessions/', tutoring_views.available_sessions, name='find_sessions'),
    path('library/', library_views.library_list, name='library'),
    path('sessions/feedback/', feedback_views.feedback, name='feedback'),
    path('update-avatar/', views.update_avatar, name='update_avatar'),
    path('update-support-needs/', views.update_support_needs, name='update_support_needs'),
]
