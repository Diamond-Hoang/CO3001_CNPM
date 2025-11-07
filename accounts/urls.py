from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('sso-login/', views.sso_login, name='sso_login'),
    path('sso/callback/', views.sso_callback, name='sso_callback'),
    path('cas/login', views.cas_login, name='cas_login'),
    path('cas/serviceValidate', views.cas_validate, name='cas_validate'),
]
