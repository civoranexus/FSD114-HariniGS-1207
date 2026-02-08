from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from courses.models import Course, Enrollment, Lesson
from certificates.models import Certificate
from accounts.models import Profile

User = get_user_model()

@login_required
def admin_dashboard(request):
    """Professional Admin Dashboard with comprehensive statistics"""
    
    # Check if user is superuser
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access Denied: Only administrators can view this page.")
    
    # Get overall statistics
    total_users = User.objects.count()
    total_students = Profile.objects.filter(role='student').count()
    total_teachers = Profile.objects.filter(role='teacher').count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_certificates = Certificate.objects.count()
    
    # Course statistics
    courses = Course.objects.annotate(
        student_count=Count('enrollments', distinct=True),
        lesson_count=Count('lessons', distinct=True),
        completion_rate=Count(
            'enrollments__progress',
            filter=Q(enrollments__progress__completed=True),
            distinct=True
        )
    ).order_by('-student_count')
    
    # User statistics - Fix: use 'enrollment' (default reverse relation for ForeignKey without related_name)
    students = User.objects.filter(profile__role='student').annotate(
        enrollment_count=Count('enrollment', distinct=True),
        certificate_count=Count('enrollment__certificate', distinct=True)
    ).order_by('-enrollment_count')[:10]
    
    teachers = User.objects.filter(profile__role='teacher').annotate(
        course_count=Count('created_courses', distinct=True),
        student_count=Count(
            'created_courses__enrollments',
            distinct=True
        )
    ).order_by('-course_count')
    
    # Recent enrollments
    recent_enrollments = Enrollment.objects.select_related('user', 'course').order_by('-enrolled_at')[:5]
    
    # Recent certificates
    recent_certificates = Certificate.objects.select_related(
        'enrollment__user',
        'enrollment__course'
    ).order_by('-issued_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_certificates': total_certificates,
        'courses': courses[:10],
        'students': students,
        'teachers': teachers,
        'recent_enrollments': recent_enrollments,
        'recent_certificates': recent_certificates,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def admin_users(request):
    """View and manage users"""
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access Denied")
    
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    
    # Filter by role if provided
    role = request.GET.get('role')
    if role:
        users = users.filter(profile__role=role)
    
    context = {
        'users': users,
        'total_users': User.objects.count(),
        'students': User.objects.filter(profile__role='student').count(),
        'teachers': User.objects.filter(profile__role='teacher').count(),
        'current_role': role,
    }
    
    return render(request, 'admin/users.html', context)


@login_required
def admin_courses(request):
    """View and manage courses"""
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access Denied")
    
    courses = Course.objects.annotate(
        student_count=Count('enrollments', distinct=True),
        lesson_count=Count('lessons', distinct=True)
    ).order_by('-id')
    
    context = {
        'courses': courses,
        'total_courses': Course.objects.count(),
    }
    
    return render(request, 'admin/courses.html', context)


@login_required
def admin_enrollments(request):
    """View enrollments"""
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Access Denied")
    
    enrollments = Enrollment.objects.select_related('user', 'course').order_by('-enrolled_at')
    
    context = {
        'enrollments': enrollments,
        'total_enrollments': Enrollment.objects.count(),
    }
    
    return render(request, 'admin/enrollments.html', context)
