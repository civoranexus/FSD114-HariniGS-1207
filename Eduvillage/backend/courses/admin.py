from django.contrib import admin
from .models import Course, Lesson, Enrollment, Progress


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')
    inlines = [LessonInline]


admin.site.register(Enrollment)
admin.site.register(Progress)




