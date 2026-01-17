from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from certificates.models import Certificate
from certificates.pdf import generate_certificate_pdf
from.models import Course,Enrollment
from .forms import EnrollmentForm
from django.http import HttpResponse
from .models import Lesson, Enrollment, Progress,LessonCompletion
from certificates.utils import sync_certificate
from django.shortcuts import redirect
from certificates.models import Certificate

def course_list(request):
    courses = Course.objects.all()
    return render(request, "courses/course_list.html", {
        "courses": courses
    })

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Get enrollment for this user & course
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    
    if not enrollment:
        # Optional: redirect or show message if not enrolled
        return redirect('courses:dashboard')

    # All lessons of the course
    lessons = Lesson.objects.filter(course=course).order_by('id')

    

    # Completed lessons ids
    completed_lessons = set(
        Progress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).values_list("lesson_id", flat=True)
    )

    certificate=Certificate.objects.filter(enrollment=enrollment).first()

    # Determine the next lesson to complete
    next_lesson_id = None
    if lessons:
        next_lesson_id = lessons.first().id
        for lesson in lessons:
            if lesson.id not in completed_lessons:
                next_lesson_id = lesson.id
                break



    return render(
        request,
        "courses/course_detail.html",
        {
            "course": course,
            "lessons": lessons,
            "enrollment": enrollment,
            "certificate": certificate,
            "completed_lessons": completed_lessons,
            "next_lesson_id": next_lesson_id,
        }
    )
   

@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(
        Certificate,
        id=certificate_id,
        enrollment__user=request.user
    )

    pdf_buffer = generate_certificate_pdf(
        certificate,
        request.user
    )

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"{certificate.enrollment.course.title}_certificate.pdf"
    )


def verify_certificate(request, verification_code):
    try:
        certificate = Certificate.objects.select_related(
            "enrollment__user",
            "enrollment__course"
        ).get(verification_code=verification_code)

        context = {
            "certificate": certificate,
            "student_name": certificate.enrollment.full_name,
            "course_name": certificate.enrollment.course.title,
            "issued_at": certificate.issued_at,
        }

    except Certificate.DoesNotExist:
        context = {"error": "Invalid Certificate ID"}

    return render(request, "certificates/verify.html", context)

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # 🔒 Prevent duplicate enrollment
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        return HttpResponse("You are already enrolled in this course.")

    if request.method == "POST":
        form = EnrollmentForm(request.POST)

        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.user = request.user
            enrollment.course = course

            # fallback name
            if not enrollment.full_name:
                enrollment.full_name = request.user.get_full_name() or request.user.username

            enrollment.save()

            return render(
                request,
                "courses/enroll_success.html",
                {"course": course}
            )

    else:
        form = EnrollmentForm()

    return render(
        request,
        "courses/enroll.html",
        {
            "form": form,
            "course": course
        }
    )



@login_required
def mark_lesson_completed(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=lesson.course
    )

    # 🔒 Enforce lesson order
    completed_lesson_ids = Progress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).values_list("lesson_id", flat=True)

    lessons_in_order = Lesson.objects.filter(
        course=lesson.course
    ).order_by("order")

    next_lesson = lessons_in_order.exclude(
        id__in=completed_lesson_ids
    ).first()

    if lesson != next_lesson:
        return HttpResponse(
            "You cannot complete this lesson yet.",
            status=403
        )

    # ✅ Mark lesson completed
    progress, _ = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    progress.completed = True
    progress.save()

    # 🎯 Check course completion
    total_lessons = lessons_in_order.count()
    completed_lessons = Progress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).count()

    # 🎓 Create certificate ONLY ONCE
    if total_lessons > 0 and completed_lessons == total_lessons:
        Certificate.objects.get_or_create(
            enrollment=enrollment
        )

    return redirect(
        "courses:course_detail",
        course_id=lesson.course.id
    )


@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(user=request.user)
    course_data = []

    for enrollment in enrollments:
        # 📚 Ordered lessons for this course
        lessons = list(
            Lesson.objects.filter(
                course=enrollment.course
            ).order_by("order")
        )

        # ✅ Completed lesson IDs for this enrollment
        completed_lessons = set(
            Progress.objects.filter(
                enrollment=enrollment,
                completed=True
            ).values_list("lesson_id", flat=True)
        )

        total_lessons = len(lessons)
        completed_count = len(completed_lessons)

        # 📊 Progress %
        progress_percent = (
            int((completed_count / total_lessons) * 100)
            if total_lessons > 0 else 0
        )

        # ⏭️ NEXT LESSON LOGIC (CRITICAL FIX)
        next_lesson_id = None

        if lessons:
            if completed_count == 0:
                # 🔓 First lesson unlocked by default
                next_lesson_id = lessons[0].id
            else:
                for lesson in lessons:
                    if lesson.id not in completed_lessons:
                        next_lesson_id = lesson.id
                        break

        # 🎓 Certificate (only exists after completion)
        certificate = Certificate.objects.filter(
            enrollment=enrollment
        ).first()

        course_data.append({
            "course": enrollment.course,
            "lessons": lessons,
            "completed_lessons": completed_lessons,
            "next_lesson_id": next_lesson_id,
            "progress_percent": progress_percent,
            "certificate": certificate,
        })

    return render(
        request,
        "courses/dashboard.html",
        {
            "course_data": course_data
        }
    )

@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    # Ensure user is enrolled
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).first()

    if not enrollment:
        return render(
            request,
            "courses/not_enrolled.html",
            {"course": course}
        )

    # ✅ FIX: Use enrollment (NOT user)
    progress, _ = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    context = {
        "course": course,
        "lesson": lesson,
        "progress": progress,
        "is_completed": progress.completed,
    }

    return render(request, "courses/lesson_detail.html", context)


