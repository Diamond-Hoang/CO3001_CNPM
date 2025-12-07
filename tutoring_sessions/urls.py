from django.urls import path
from . import views

app_name = 'tutoring_sessions'

urlpatterns = [
    path('', views.session_list, name='session_list'),
    path('enrollment/<int:enrollment_id>/cancel/', views.cancel_enrollment, name='cancel_enrollment'),
    path('available/', views.available_sessions, name='available_sessions'),
    path('<int:session_id>/enroll/', views.enroll_session, name='enroll_session'),
    path('reschedule/<int:enrollment_id>/', views.reschedule_session, name='reschedule_session'),
    path('tutor/sessions/<int:session_id>/reschedule/', views.tutor_reschedule_session, name='tutor_reschedule_session'),
    path('tutor/sessions/<int:session_id>/students/', views.view_session_students, name='view_students'),
    path('tutor/sessions/<int:session_id>/cancel/', views.tutor_cancel_session, name='tutor_cancel_session'),
]