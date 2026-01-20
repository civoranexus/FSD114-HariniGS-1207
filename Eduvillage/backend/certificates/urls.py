from django.urls import path
from . import views

app_name = "certificates"

urlpatterns = [

    # 🔍 Certificate Verification
    path(
        "verify/",
        views.verify_certificate,
        name="verify_form"
    ),
    path(
        "verify/<uuid:verification_code>/",
        views.verify_certificate,
        name="verify_certificate"
    ),

    # 📄 Certificate Views
    path(
        "certificate/<int:pk>/",
        views.certificate_detail,
        name="certificate_detail"
    ),
    path(
        "view/<int:course_id>/",
        views.view_certificate,
        name="view"
    ),
    path(
        "download/<int:certificate_id>/",
        views.download_certificate,
        name="download_certificate"
    ),

    # 👤 User
    path(
        "my/",
        views.my_certificates,
        name="my_certificates"
    ),

    # 🛠 Admin
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),
]
