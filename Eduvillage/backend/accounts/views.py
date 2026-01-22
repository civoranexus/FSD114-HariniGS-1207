from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def role_login(request, role):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            if user.profile.role == role:
                login(request, user)

                if role == 'admin':
                    return redirect('certificates:admin_dashboard')
                elif role == 'teacher':
                    return redirect('courses:teacher_dashboard')
                else:
                    return redirect('courses:student_dashboard')
            else:
                messages.error(request, "Unauthorized role access")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'accounts/login.html', {'role': role})
