from django.urls import path
from .views import role_login

app_name = 'accounts'

urlpatterns = [
    path('login/<str:role>/', role_login, name='role_login'),
]
