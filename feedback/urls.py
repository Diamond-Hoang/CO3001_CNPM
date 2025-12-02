from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('enrollment/<int:enrollment_id>/feedback/', views.feedback, name='feedback'),
    path('sessions/request_session/', views.request_session, name='request_session'), 
    path('technical_report/', views.technical_report, name='technical_report'), 
    path('session/<int:session_id>/feedback/', views.view_feedback, name='view_feedback'),
]