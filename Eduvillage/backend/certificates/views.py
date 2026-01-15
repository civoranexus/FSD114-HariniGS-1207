from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Certificate
from .pdf import generate_certificate_pdf
from django.http import HttpResponse
from django.contrib import messages
from courses.models import Course, Enrollment, Lesson, Progress
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required


@login_required
def download_certificate(request, course_id):
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course_id=course_id
    ).first()

    if not enrollment:
        return HttpResponse("You are not enrolled in this course.", status=403)

    total_lessons = Lesson.objects.filter(course=enrollment.course).count()
    completed_lessons = Progress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).count()

    if completed_lessons < total_lessons:
        messages.warning(
            request,
            "⚠ Complete all lessons to download your certificate."
        )
        return redirect("courses:dashboard")

    # Create or get certificate
    certificate, created = Certificate.objects.get_or_create(enrollment=enrollment)

    # ✅ Mark as downloaded
    if not certificate.downloaded:
        certificate.downloaded = True
        certificate.save()

    # Generate PDF
    pdf_buffer = generate_certificate_pdf(certificate)

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
        enrollment = certificate.enrollment
        user = enrollment.user

        student_name = enrollment.full_name.strip() if enrollment.full_name else ""
        if not student_name:
            student_name = user.get_full_name().strip()
        if not student_name:
            student_name = user.username

        context = {
            "certificate": certificate,
            "student_name": certificate.enrollment.full_name,
            "course_name": certificate.enrollment.course.title,
            "issued_at": certificate.issued_at,
        }

    except Certificate.DoesNotExist:
        context["error"] = "Invalid Certificate ID"

    return render(request, "certificates/verify.html", context)

@login_required
def view_certificate(request, course_id):
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course_id=course_id
    ).first()

    if not enrollment:
        return HttpResponse("Not enrolled", status=403)

    certificate = Certificate.objects.filter(
        enrollment=enrollment
    ).first()

    if not certificate:
        return redirect("courses:dashboard")

    return render(
        request,
        "certificates/certificate.html",
        {"certificate": certificate}
    )

@login_required
def my_certificates(request):
    certificates = Certificate.objects.select_related(
        "enrollment__course"
    ).filter(
        enrollment__user=request.user
    ).order_by("-issued_at")

    return render(
        request,
        "certificates/my_certificates.html",
        {"certificates": certificates}
    )

@staff_member_required
def admin_dashboard(request):
    enrollments = Enrollment.objects.select_related("user", "course")
    students_data = []

    for enrollment in enrollments:
        total_lessons = Lesson.objects.filter(course=enrollment.course).count()

        completed_lessons = Progress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).count()

        certificate = Certificate.objects.filter(enrollment=enrollment).first()

        students_data.append({
            "student": enrollment.user.username,
            "full_name": enrollment.full_name,
            "course": enrollment.course.title,
            "progress": f"{completed_lessons}/{total_lessons}",
            "certificate_issued": "Yes" if certificate else "No",
            "certificate_downloaded": "Yes" if certificate and certificate.downloaded else "No",
        })

    return render(
        request,
        "certificates/admin_dashboard.html",
        {"students_data": students_data}
    )

