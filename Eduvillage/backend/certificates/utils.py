from certificates.models import Certificate
from courses.models import Lesson
from courses.models import Progress
from courses.models import Enrollment
from certificates.models import Certificate
from courses.models import Enrollment, Lesson, Progress


def sync_certificate(user, course):
    total_lessons = Lesson.objects.filter(course=course).count()

    completed_lessons = Progress.objects.filter(
        student=user,
        lesson__course=course,
        completed=True
    ).count()

    # Safety check
    if total_lessons == 0:
        return

    # Only proceed if fully completed
    if total_lessons != completed_lessons:
        return

    try:
        enrollment = Enrollment.objects.get(
            user=user,   # ✅ match field name
            course=course
        )
    except Enrollment.DoesNotExist:
        return

    Certificate.objects.get_or_create(
        student=user,
        course=course,
        enrollment=enrollment
    )