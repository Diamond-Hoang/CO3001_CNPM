from django.urls import path
from . import views

app_name = "library"

urlpatterns = [
    path('library', views.library_list, name="list"),
]
