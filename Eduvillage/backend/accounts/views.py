from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import LoginForm
from .models import Profile
from courses.models import Enrollment, Course, LessonCompletion, Lesson, Progress

User = get_user_model()

def role_login(request):
    """Login view with role-based authentication and redirection"""
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Allow superusers/staff to login with 'admin' role
                if user.is_superuser and role == 'admin':
                    login(request, user)
                    messages.success(request, f"Login successful! Welcome {username} 🎉")
                    return redirect_to_dashboard(user)
                
                # For non-admin users, verify role matches user's profile
                try:
                    profile = Profile.objects.get(user=user)
                    if profile.role != role:
                        messages.error(request, "Invalid role for this user.")
                        return redirect('accounts:role_login')
                except Profile.DoesNotExist:
                    messages.error(request, "User profile not found.")
                    return redirect('accounts:role_login')
                
                login(request, user)
                messages.success(request, f"Login successful! Welcome {username} 🎉")
                return redirect_to_dashboard(user)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def register(request):
    """Register view for new users"""
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
    
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        role = request.POST.get('role')
        
        # Validation
        if not all([username, email, password, password_confirm, role]):
            messages.error(request, "All fields are required.")
            return redirect('accounts:register')
        
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('accounts:register')
        
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return redirect('accounts:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('accounts:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('accounts:register')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Update the profile created by signal with the role
            profile = Profile.objects.get(user=user)
            profile.role = role
            profile.save()
            
            messages.success(request, "Registration successful! Please login with your credentials.")
            return redirect('accounts:role_login')
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return redirect('accounts:register')
    
    return render(request, 'accounts/register.html')

def redirect_to_dashboard(user):
    """Redirect user to their role-specific dashboard"""
    # Superusers/staff go to admin dashboard
    if user.is_superuser:
        return redirect('admin:index')
    
    try:
        profile = Profile.objects.get(user=user)
        
        if profile.role == 'student':
            return redirect('courses:student_dashboard')
        elif profile.role == 'teacher':
            return redirect('courses:teacher_dashboard')
        elif profile.role == 'admin':
            return redirect('admin:index')
    except Profile.DoesNotExist:
        return redirect('home')
    
    return redirect('home')

@login_required(login_url='accounts:role_login')
def logout_view(request):
    """Logout view that clears user session"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


@login_required(login_url='accounts:role_login')
def student_profile(request):
    user = request.user

    # Verify student role
    try:
        profile = Profile.objects.get(user=user)
        if profile.role != 'student':
            return redirect('home')
    except Profile.DoesNotExist:
        return redirect('home')

    # Get enrollments
    enrollments = Enrollment.objects.filter(user=user).select_related('course')

    # Certificates
    certificates = [
        enrollment.certificate
        for enrollment in enrollments
        if hasattr(enrollment, 'certificate')
    ]

    courses_in_progress = []
    completed_courses = []

    total_lessons_completed = 0

    for enrollment in enrollments:
        course = enrollment.course

        total_lessons = Lesson.objects.filter(
            course=course,
            is_active=True
        ).count()

        completed = Progress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).count()

        total_lessons_completed += completed

        progress_percent = (
            round((completed / total_lessons) * 100, 0)
            if total_lessons > 0 else 0
        )

        progress_data = {
            'course': course,
            'completed': completed,
            'total': total_lessons,
            'progress_percent': progress_percent
        }

        if completed >= total_lessons and total_lessons > 0:
            completed_courses.append(progress_data)
        else:
            courses_in_progress.append(progress_data)

    # Sort in-progress courses by progress
    courses_in_progress.sort(
        key=lambda x: x['progress_percent'],
        reverse=True
    )

    context = {
        'user': user,
        'profile': profile,
        'courses_in_progress': courses_in_progress,
        'completed_courses': completed_courses,
        'certificates': certificates,
        'total_lessons_completed': total_lessons_completed,
        'total_courses_enrolled': enrollments.count(),
        'total_certificates': len(certificates),
    }

    return render(request, 'accounts/student_profile.html', context)