from django.urls import path
from .import views 
from .views import course_list, course_detail, dashboard_router, enroll_course
from .views import mark_lesson_completed

app_name = "courses"

urlpatterns = [
    path('list/', views.course_list, name='course_list'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path("course/<int:course_id>/lesson/<int:lesson_id>/", views.lesson_detail, name='lesson_detail'),
    path("certificates/download/<int:course_id>/", views.download_certificate, name="download_certificate"),
    path("lesson/<int:lesson_id>/complete/",views.mark_lesson_completed,name="mark_lesson_completed"),
    path('course/<int:course_id>/add-lesson/', views.add_lesson, name='add_lesson'),
    path('lesson/<int:lesson_id>/edit/', views.edit_lesson, name='edit_lesson'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path("course/create/", views.create_course, name="create_course"),
    path(
    "teacher/course/<int:course_id>/",
    views.teacher_course_detail,
    name="teacher_course_detail"),
    path("", views.home, name="home"),
    path("dashboard/", dashboard_router, name="dashboard_router"),
    





]
