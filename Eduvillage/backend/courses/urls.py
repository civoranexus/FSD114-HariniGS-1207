from django.urls import path
from .import views 
from .views import course_list, course_detail, enroll_course
from .views import mark_lesson_completed

app_name = "courses"

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('', course_list, name='course_list'),
    path('<int:course_id>/', course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', enroll_course, name='enroll_course'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.mark_lesson_completed, name='mark_lesson_completed'),
    path("course/<int:course_id>/lesson/<int:lesson_id>/", views.lesson_detail, name='lesson_detail'),
    path("certificates/download/<int:course_id>/", views.download_certificate, name="download_certificate"),
    path("lesson/<int:lesson_id>/complete/",views.mark_lesson_completed,name="mark_lesson_completed"),
]
