from .models import Enrollment, Lesson
from.models import Enrollment, Certificate
from courses.models import Progress

def sync_certificate(user, course):
    enrollment = Enrollment.objects.filter(
        user=user,
        course=course
    ).first()

    if not enrollment:
        return

    Certificate.objects.get_or_create(
        enrollment=enrollment
    )


def check_course_completion(user, course):
    total_lessons = Lesson.objects.filter(course=course).count()

    completed_lessons = Progress.objects.filter(
        student=user,
        lesson__course=course,
        completed=True
    ).count()

    return total_lessons > 0 and completed_lessons == total_lessons
