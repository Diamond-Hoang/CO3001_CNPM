from django.urls import path
from . import views

app_name='tutors'

urlpatterns = [
    path('dashboard/', views.dashboard, name='tutor_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('sessions/', views.sessions, name='sessions'),
    path('sessions/material/<int:session_id>/', views.session_materials, name='session_materials'),
    path('update-avatar/', views.update_avatar, name='update_avatar'),
    path('update-expertise/', views.update_expertise, name='update_expertise'),
    path('availability/', views.availability_schedule, name='availability_schedule'),
    path('availability/set/', views.set_availability, name='set_availability'),
    path('availability/delete/', views.delete_availability, name='delete_availability'),
    path('availability/debug/', views.availability_schedule_debug, name='availability_schedule_debug'),
    path('student/<int:student_id>/session/<int:session_id>/progress/', views.student_progress, name='student_progress'),
    path('advising/create/', views.create_advising_session, name='create_advising_session'),
]
