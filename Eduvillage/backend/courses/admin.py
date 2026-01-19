from django.contrib import admin
from .models import Course, Lesson, Enrollment, Progress


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description')
    search_fields = ('title',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course')
    list_filter = ('course',)
    fields = ("course", "title", "content", "video", "order")
    list_display = ("title", "course", "order")



@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'enrolled_at')
    list_filter = ('course',)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment', 'lesson', 'completed')
    list_filter = ('completed',)


   
