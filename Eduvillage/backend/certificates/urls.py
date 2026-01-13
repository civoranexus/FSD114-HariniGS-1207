from django.urls import path
from . import views

app_name = "certificates"

urlpatterns = [
    path("download/<int:course_id>/", views.download_certificate, name="download_certificate"),
    path("verify/", views.verify_certificate, name="verify_certificate"),
     path(
        "verify/<str:certificate_id>/",
        views.verify_certificate,
        name="verify_certificate"
    ),

]

