from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='student_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('sessions/', views.sessions, name='sessions'),
    path('sessions/material/', views.session_material, name='session_material'),
    path('find_sessions/', views.find_sessions, name='find_sessions'),
    path('library/', views.library, name='library'),
    path('sessions/feedback/', views.feedback, name='feedback'),
    path('sessions/request_session/', views.request_session, name='request_session'),
    path('technical_report/', views.technical_report, name='technical_report'),
]
