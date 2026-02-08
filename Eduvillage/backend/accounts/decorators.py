from django.shortcuts import redirect

def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role != 'student':
            return redirect('courses:home')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('courses:home')
        return view_func(request, *args, **kwargs)
    return wrapper
