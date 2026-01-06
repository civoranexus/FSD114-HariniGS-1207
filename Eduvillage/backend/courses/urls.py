from django.urls import path
from .import views 
from .views import course_list, course_detail, enroll_course
urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('', course_list, name='course_list'),
    path('<int:course_id>/', course_detail, name='course_detail'),
    path('<int:course_id>/enroll/', enroll_course, name='enroll_course'),
]
