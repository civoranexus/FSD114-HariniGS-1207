from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment
from .forms import EnrollmentForm


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
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'enrolled': enrolled
    })



@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Prevent duplicate enrollment
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return HttpResponse("You are already enrolled")

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = request.user
            enrollment.course = course
            enrollment.save()
            return render(request, 'courses/enroll_success.html', {'course': course})
    else:
        form = EnrollmentForm()

    return render(request, 'courses/enroll.html', {
        'form': form,
        'course': course
    })
