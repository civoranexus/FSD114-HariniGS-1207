from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path("login/", views.role_login, name="role_login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),
]
