import profile
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
from .forms import LessonForm
from django.db import models



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
        return redirect("courses:enroll_course", course_id=course.id)


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



from certificates.models import Certificate

@login_required
def mark_lesson_completed(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=lesson.course
    )

    # Mark progress
    progress, _ = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    progress.completed = True
    progress.save()

    # Check if all lessons are completed
    total_lessons = Lesson.objects.filter(course=lesson.course).count()
    completed_lessons = Progress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).count()

    if total_lessons == completed_lessons:
        # ✅ Create or get certificate
        certificate, _ = Certificate.objects.get_or_create(
            enrollment=enrollment
        )

        # ✅ Redirect to certificate page
        return redirect(
            "certificates:certificate_detail",
            certificate.id
        )

    # Otherwise go back to lesson
    return redirect(
        "courses:lesson_detail",
        lesson.course.id,
        lesson.id
    )


@login_required
def student_dashboard(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'student':
        return redirect('courses:home')

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
            "course_data": course_data,
             'enrollments': enrollments
        }
    )

@login_required
def lesson_detail(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).first()

    if not enrollment:
        return render(request, "courses/not_enrolled.html")

    lessons = list(
        Lesson.objects.filter(course=course).order_by("order")
    )

    progress_qs = Progress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).values_list("lesson_id", flat=True)

    completed_lessons = set(progress_qs)

    # 🔓 Unlock logic
    unlocked_lessons = set()
    if lessons:
        unlocked_lessons.add(lessons[0].id)  # First lesson always unlocked
        for lesson_obj in lessons:
            if lesson_obj.id in completed_lessons:
                unlocked_lessons.add(lesson_obj.id)
            else:
                break

    current_index = lessons.index(lesson)

    prev_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = (
        lessons[current_index + 1]
        if current_index < len(lessons) - 1
        else None
    )

    progress, _ = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    context = {
        "course": course,
        "lesson": lesson,
        "lessons": lessons,
        "completed_lessons": completed_lessons,
        "unlocked_lessons": unlocked_lessons,
        "prev_lesson": prev_lesson,
        "next_lesson": next_lesson,
        "progress": progress,
    }

    return render(request, "courses/lesson_detail.html", context)
def home(request):
    courses = Course.objects.all()[:6]  # show limited courses
    return render(request, "home.html", {"courses": courses})

@login_required
def teacher_dashboard(request):
    if request.user.profile.role != 'teacher' and not request.user.is_staff:
        return redirect('courses:home')

    courses = Course.objects.filter(created_by=request.user)
    return render(request, 'courses/teacher_dashboard.html', {'courses': courses})



@login_required
def add_lesson(request, course_id):
    if not request.user.is_staff:
        return redirect("courses:home")

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "")
        video = request.FILES.get("video")

        if not title:
            return render(
                request,
                "courses/add_lesson.html",
                {
                    "course": course,
                    "error": "Lesson title is required."
                }
            )

        # 🔢 Auto-calculate lesson order
        last_order = (
            Lesson.objects
            .filter(course=course)
            .aggregate(models.Max("order"))["order__max"]
        )

        next_order = (last_order or 0) + 1

        Lesson.objects.create(
            course=course,
            title=title,
            content=content,
            video=video,
            order=next_order
        )

        return redirect("courses:course_detail", course_id=course.id)

    return render(request, "courses/add_lesson.html", {"course": course})

@login_required
def dashboard_router(request):
    role = request.user.profile.role

    if role == "student":
        return redirect("courses:student_dashboard")
    elif role == "teacher":
        return redirect("courses:teacher_dashboard")
    elif request.user.is_staff:
        return redirect("/admin/")
    else:
        return redirect("courses:home")
    
@login_required
def create_course(request):

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        Course.objects.create(
            title=title,
            description=description,
            created_by=request.user
        )

        return redirect("courses:teacher_dashboard")

    return render(request, "courses/create_course.html")

@login_required
def teacher_course_detail(request, course_id):
    

    course = get_object_or_404(
        Course,
        id=course_id,
        created_by=request.user
    )

    lessons = course.lessons.all()

    return render(
        request,
        "courses/teacher_course_detail.html",
        {
            "course": course,
            "lessons": lessons,
        }
    )









