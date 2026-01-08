from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment
from .forms import EnrollmentForm
from .models import Enrollment, Progress,Lesson


@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrolled = Enrollment.objects.filter(
        course=course,
        student=request.user
    ).exists()
    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists()
    lessons = course.lessons.all() if is_enrolled else []
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'enrolled': enrolled,
        'lessons': lessons
    })

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Prevent duplicate enrollment
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return HttpResponse("You are already enrolled in this course.")

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            # Save enrollment but don't commit yet
            enrollment = form.save(commit=False)
            
            # Ensure student and course are set correctly
            enrollment.student = request.user
            enrollment.course = course

            # If full_name not provided, fallback to user's full name or username
            if not enrollment.full_name:
                enrollment.full_name = request.user.get_full_name() or request.user.username

            # If phone_number not provided, put placeholder
            if not enrollment.phone_number:
                enrollment.phone_number = "0000000000"

            enrollment.save()
            
            # Optional: create initial progress objects for each lesson
            # for lesson in course.lessons.all():
            #     Progress.objects.create(student=request.user, lesson=lesson, completed=False)

            return render(request, 'courses/enroll_success.html', {'course': course})
        else:
            # Form invalid: show errors
            return render(request, 'courses/enroll.html', {'form': form, 'course': course})
    else:
        # GET request: show blank form
        form = EnrollmentForm()
        return render(request, 'courses/enroll.html', {'form': form, 'course': course})

@login_required
def mark_lesson_completed(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    progress, _ = Progress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )

    progress.completed = True
    progress.save()

    return redirect('student_dashboard')


@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user)

    dashboard_data = []
    progress_data = {}

    # Get all completed lesson IDs for this student (ONCE)
    completed_lessons = Progress.objects.filter(
        student=request.user,
        completed=True
    ).values_list('lesson_id', flat=True)

    for enrollment in enrollments:
        course = enrollment.course
        total_lessons = course.lessons.count()

        completed_count = Progress.objects.filter(
            student=request.user,
            lesson__course=course,
            completed=True
        ).count()

        dashboard_data.append({
            'course': course,
            'total': total_lessons,
            'completed': completed_count,
            'lessons': course.lessons.all(),
        })

        progress_data[course.id] = {
            'total': total_lessons,
            'completed': completed_count
        }

    # ✅ ONE context
    context = {
        'dashboard_data': dashboard_data,
        'progress_data': progress_data,
        'enrollments': enrollments,
        'completed_lessons': completed_lessons,
    }

    # ✅ ONE return at the END
    return render(request, 'courses/dashboard.html', context)

    return render(request, 'courses/dashboard.html', context)


    