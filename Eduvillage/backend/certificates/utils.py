from certificates.models import Certificate
from courses.models import Lesson
from courses.models import Progress

def sync_certificate(user, course):
    total_lessons = Lesson.objects.filter(course=course).count()
    completed_lessons = Progress.objects.filter(
        student=user,
        lesson__course=course,
        completed=True
    ).count()

    if total_lessons > 0 and total_lessons == completed_lessons:
        Certificate.objects.get_or_create(
            user=user,
            course=course
        )
    else:
        Certificate.objects.filter(
            user=user,
            course=course
        ).delete()
