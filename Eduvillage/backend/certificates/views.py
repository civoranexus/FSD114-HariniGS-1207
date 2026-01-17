from multiprocessing import context
from urllib import request
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Certificate
from .pdf import generate_certificate_pdf
from django.http import HttpResponse
from django.contrib import messages
from courses.models import  Enrollment, Lesson, Progress
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required




@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        enrollment__user=request.user
    )

    enrollment = certificate.enrollment

    # ✅ Check completion FIRST
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

    # ❌ REMOVE this block (this was breaking everything)
    # if certificate.downloaded:
    #     return HttpResponse("Certificate already downloaded.", status=403)

    # ✅ Generate PDF
    pdf_buffer = generate_certificate_pdf(certificate)

    # ✅ Mark downloaded ONLY AFTER GENERATING
    if not certificate.downloaded:
        certificate.downloaded = True
        certificate.save()

    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{certificate.verification_code}.pdf"'
    )

    return response




def verify_certificate(request, verification_code=None):
    if request.method == "GET" and verification_code is None:
        return render(request, "certificates/verify_form.html")

    # 1️⃣ POST request → verification from form
    if request.method == "POST":
        verification_code = request.POST.get("verification_code","").strip()

        if not verification_code:
            return render(
                request,
                "certificates/verify_form.html",
                {"error": "Please enter a certificate ID"}
            )

    # 2️⃣ If verification code exists (from URL or POST)
    if verification_code:
        certificate = Certificate.objects.select_related(
            "enrollment__user",
            "enrollment__course"
        ).filter(verification_code=verification_code).first()

        if not certificate:
            return render(
                request,
                "certificates/verify_result.html",
                {"error": "Invalid Certificate ID"}
            )

        enrollment = certificate.enrollment
        user = enrollment.user

        student_name = (
            enrollment.full_name
            or user.get_full_name()
            or user.username
        )

        context = {
            "certificate": certificate,
            "student_name": student_name,
            "course_name": enrollment.course.title,
            "issued_at": certificate.issued_at,
        }

        return render(request, "certificates/verify_result.html", context)

    # 3️⃣ GET request → show form
    return render(request, "certificates/verify_form.html")


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

