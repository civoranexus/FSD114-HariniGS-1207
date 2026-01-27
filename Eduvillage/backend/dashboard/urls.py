from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.admin_users, name='admin_users'),
    path('courses/', views.admin_courses, name='admin_courses'),
    path('enrollments/', views.admin_enrollments, name='admin_enrollments'),
]
