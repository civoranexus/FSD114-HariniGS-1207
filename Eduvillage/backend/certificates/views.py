from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Certificate
from .pdf import generate_certificate_pdf
from django.http import HttpResponse
from django.contrib import messages
from courses.models import Course, Enrollment, Lesson, Progress
from django.shortcuts import redirect


@login_required
def download_certificate(request, course_id):
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course_id=course_id
    ).first()

    if not enrollment:
        return HttpResponse("You are not enrolled in this course.", status=403)

    # ✅ FIX: define course
    course = enrollment.course
    # total lessons in the course
    total_lessons = Lesson.objects.filter(
        course=enrollment.course
    ).count()

    # completed lessons by THIS enrollment
    completed_lessons = Progress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).count()

    # 🔍 Total lessons
    total_lessons = Lesson.objects.filter(course=course).count()

    # 🔍 Completed lessons
    completed_lessons = Progress.objects.filter(
    enrollment=enrollment,
    lesson__course=course,
    completed=True
).count()

    # ❌ Block download if not completed
    if completed_lessons < total_lessons:
        messages.warning(
            request,
            "⚠ Complete all lessons to download your certificate."
        )
        return redirect("courses:dashboard")

    # ✅ Certificate (create if not exists)
    certificate, created = Certificate.objects.get_or_create(
        enrollment=enrollment
    )

    # 📄 Generate PDF
    pdf_buffer = generate_certificate_pdf(
        user=request.user,
        certificate=certificate
    )

    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=certificate.pdf"
    return response


def verify_certificate(request, verification_code):
    context = {}

    try:
        certificate = Certificate.objects.select_related(
            "enrollment__user",
            "enrollment__course"
        ).get(verification_code=verification_code)

        context = {
            "certificate": certificate,
            "student_name": certificate.enrollment.full_name
            or certificate.enrollment.user.get_full_name()
            or certificate.enrollment.user.username,
            "course_name": certificate.enrollment.course.title,
            "issued_at": certificate.issued_at,
        }

    except Certificate.DoesNotExist:
        context["error"] = "Invalid Certificate ID"

    return render(request, "certificates/verify.html", context)


