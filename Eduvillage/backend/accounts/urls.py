from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    path('login/<str:role>/', views.role_login, name='role_login'),
    path(
        "logout/",
        LogoutView.as_view(next_page="accounts:login_teacher"),
        name="logout"
    ),


    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path("redirect/", views.role_redirect, name="role_redirect"),

]
