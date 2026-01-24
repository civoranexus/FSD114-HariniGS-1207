from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def role_redirect(request):
    role = request.user.profile.role

    if role == "student":
        return redirect("courses:student_dashboard")
    elif role == "teacher":
        return redirect("courses:teacher_dashboard")
    elif role == "admin":
        return redirect("courses:admin_dashboard")

    return redirect("home")

def role_login(request, role):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on role
            if role == "student":
                return redirect("courses:student_dashboard")
            elif role == "teacher":
                return redirect("courses:teacher_dashboard")
            elif role == "admin":
                return redirect("/admin/")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "accounts/role_login.html", {"role": role})

    
def student_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user and user.profile.role == "student":
            login(request, user)
            return redirect("student_dashboard")
        else:
            messages.error(request, "Invalid student credentials")

    return render(request, "accounts/login_student.html")


def teacher_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user and user.profile.role == "teacher":
            login(request, user)
            return redirect("teacher_dashboard")
        else:
            messages.error(request, "Invalid teacher credentials")

    return render(request, "accounts/login_teacher.html")

def logout_view(request):
    logout(request)
    return redirect("role_login", role="student")

@login_required
def student_dashboard(request):
    if request.user.profile.role != 'student':
        return redirect('accounts:role_login', role='student')

    return render(request, 'accounts/student_dashboard.html')


def logout_view(request):
    logout(request)
    return redirect("login_teacher")



