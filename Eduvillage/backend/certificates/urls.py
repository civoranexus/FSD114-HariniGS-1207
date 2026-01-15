from django.urls import path
from . import views

app_name = "certificates"

urlpatterns = [
    path("download/<int:course_id>/", views.download_certificate, name="download_certificate"),
     path(
        "verify/<uuid:verification_code>/",
        views.verify_certificate,
        name="verify_certificate"
    ),
    path("view/<int:course_id>/", views.view_certificate, name="view"),
    path("my/", views.my_certificates, name="my_certificates"),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]

