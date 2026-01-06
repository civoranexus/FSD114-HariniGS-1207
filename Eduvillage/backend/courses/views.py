from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment


@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses})


@login_required
def enroll_course(request, course_id):
    course = Course.objects.get(id=course_id)

    if request.user.role != 'student':
        return HttpResponse("Only students can enroll")

    Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )
    return redirect('course_list')
