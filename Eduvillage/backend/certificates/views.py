from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,render
from courses.models import Enrollment
from .models import Certificate
from .pdf import generate_certificate_pdf


@login_required
def download_certificate(request, course_id):
    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course_id=course_id
    )

    certificate = get_object_or_404(
        Certificate,
        enrollment=enrollment
    )

    return FileResponse(
        generate_certificate_pdf(certificate),
        as_attachment=True,
        filename=f"{certificate.enrollment.course.title}_certificate.pdf",
    )

def verify_certificate(request):
    certificate_id = request.GET.get("cid", "").strip()

    context = {}

    if certificate_id:
        try:
            certificate = Certificate.objects.select_related(
                "student", "course"
            ).get(certificate_id=certificate_id)

            context.update({
                "certificate": certificate,
                "student_name": certificate.student.get_full_name()
                or certificate.student.username,
                "course_name": certificate.course.title,
                "issued_at": certificate.issued_at,
            })

        except Certificate.DoesNotExist:
            context["error"] = "Invalid Certificate ID"

    else:
        context["error"] = "Certificate ID is required"

    return render(request, "certificates/verify.html", context)

   

    
