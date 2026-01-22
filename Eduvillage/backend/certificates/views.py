
from urllib import request
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Certificate
from .pdf import generate_certificate_pdf
from django.http import HttpResponse
from django.contrib import messages
from courses.models import  Course, Enrollment, Lesson, Progress
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required




@login_required
def download_certificate(request, pk):
    certificate = get_object_or_404(
        Certificate,
        id=pk,
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

    # ✅ Generate PDF
    pdf_buffer = generate_certificate_pdf(certificate)

    # ✅ Mark downloaded AFTER generating
    if not certificate.downloaded:
        certificate.downloaded = True
        certificate.save()

    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="certificate_{certificate.id}.pdf"'
    )

    return response





def verify_certificate(request, verification_code=None):
    # 1️⃣ Show verify form (GET without code)
    if request.method == "GET" and not verification_code:
        return render(request, "certificates/verify_form.html")

    # 2️⃣ Handle form submission (POST)
    if request.method == "POST":
        verification_code = (
            request.POST.get("verification_code", "").strip()
        )

        if not verification_code:
            return render(
                request,
                "certificates/verify_form.html",
                {"error": "Please enter a certificate ID"}
            )

    # 3️⃣ Lookup certificate (URL or POST)
    certificate = (
        Certificate.objects
        .select_related("enrollment__user", "enrollment__course")
        .filter(verification_code=verification_code)
        .first()
    )

    # ❌ Invalid certificate
    if not certificate:
        return render(
            request,
            "certificates/verify_result.html",
            {
                "status": "invalid",
                "message": "Invalid Certificate ID"
            }
        )

    enrollment = certificate.enrollment
    user = enrollment.user

    student_name = (
        enrollment.full_name
        or user.get_full_name()
        or user.username
    )

    # 4️⃣ Revoked certificate check
    if certificate.revoked:
        return render(
            request,
            "certificates/verify_result.html",
            {
                "status": "revoked",
                "student_name": student_name,
                "course_name": enrollment.course.title,
                "issued_at": certificate.issued_at,
            }
        )

    # 5️⃣ Valid certificate
    return render(
        request,
        "certificates/verify_result.html",
        {
            "status": "valid",
            "certificate": certificate,
            "student_name": student_name,
            "course_name": enrollment.course.title,
            "issued_at": certificate.issued_at,
        }
    )



@login_required
def view_certificate(request, course_id):
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course_id=course_id
    ).first()

    if request.user.is_staff:
        return redirect('courses:home')


    if not enrollment:
        return HttpResponse("Not enrolled", status=403)

    certificate = Certificate.objects.filter(
        enrollment=enrollment
    ).first()
    if certificate.revoked:
        return render(
        request,
        "certificates/verify_result.html",
        {
            "status": "revoked",
            "certificate": certificate
        }
    )

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
    if not request.user.is_staff:
        return redirect('courses:home')
    
    certificates = Certificate.objects.select_related(
        "enrollment",
        "enrollment__user",
        "enrollment__course"
    )

    # 🔍 Search by student name or username
    query = request.GET.get("q")
    if query:
        certificates = certificates.filter(
            enrollment__full_name__icontains=query
        ) | certificates.filter(
            enrollment__user__username__icontains=query
        )

    # 🎓 Filter by course
    course_id = request.GET.get("course")
    if course_id:
        certificates = certificates.filter(
            enrollment__course__id=course_id
        )

    # ⬇ Downloaded filter
    downloaded = request.GET.get("downloaded")
    if downloaded == "true":
        certificates = certificates.filter(downloaded=True)
    elif downloaded == "false":
        certificates = certificates.filter(downloaded=False)

    # 🚫 Revoked filter
    revoked = request.GET.get("revoked")
    if revoked == "true":
        certificates = certificates.filter(revoked=True)
    elif revoked == "false":
        certificates = certificates.filter(revoked=False)

    courses = Course.objects.all()

    return render(
        request,
        "certificates/admin_dashboard.html",
        {
            "students_data": certificates,
            "courses": courses,
            "query": query,
        }
    )


@login_required
def certificate_detail(request, pk):
    certificate = get_object_or_404(Certificate, id=pk, enrollment__user=request.user)
    enrollment = certificate.enrollment
    course = enrollment.course
    total_lessons = Lesson.objects.filter(course=course).count()
    completed_lessons = Progress.objects.filter(
        enrollment=enrollment, completed=True
    ).count()
    is_completed = completed_lessons == total_lessons
    context = {
        "certificate": certificate,
        "course": course,
        "is_completed": is_completed,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
    }
    return render(request, "certificates/certificate_detail.html", context)

@staff_member_required
def revoke_certificate(request, pk):
    cert = get_object_or_404(Certificate, id=pk)
    cert.revoked = True
    cert.save()
    return redirect("certificates:admin_dashboard")


@staff_member_required
def reissue_certificate(request, pk):
    cert = get_object_or_404(Certificate, id=pk)
    cert.revoked = False
    cert.save()
    return redirect("certificates:admin_dashboard")




