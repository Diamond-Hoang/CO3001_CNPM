from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.dashboard, name='student_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('sessions/', views.sessions, name='sessions'),
    path('sessions/material/<int:session_id>/', views.session_material, name='session_material'),  # ← THÊM session_id
    path('find_sessions/', views.find_sessions, name='find_sessions'),
    path('library/', views.library, name='library'),
    path('sessions/feedback/', views.feedback, name='feedback'),
]
