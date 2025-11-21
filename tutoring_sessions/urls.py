from django.urls import path
from . import views

app_name = 'tutoring_sessions'

urlpatterns = [
    path('', views.session_list, name='session_list'),
    path('<int:session_id>/', views.session_detail, name='session_detail'),
    path('<int:session_id>/materials/', views.session_materials, name='session_materials'),
    path('enrollment/<int:enrollment_id>/cancel/', views.cancel_enrollment, name='cancel_enrollment'),
    path('enrollment/<int:enrollment_id>/feedback/', views.feedback, name='feedback'),
    path('available/', views.available_sessions, name='available_sessions'),
    path('<int:session_id>/enroll/', views.enroll_session, name='enroll_session'),
]