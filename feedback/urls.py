from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('enrollment/<int:enrollment_id>/feedback/', views.feedback, name='feedback'),
]