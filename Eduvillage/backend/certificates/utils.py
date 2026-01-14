from courses.models import Enrollment, Lesson, Progress
from certificates.models import Certificate

def sync_certificate(user, course):
    try:
        enrollment = Enrollment.objects.get(student=user, course=course)
    except Enrollment.DoesNotExist:
        return

    total_lessons = Lesson.objects.filter(course=course).count()
    completed_lessons = Progress.objects.filter(
        user=user,
        lesson__course=course,
        completed=True
    ).count()

    if total_lessons == completed_lessons and total_lessons > 0:
        Certificate.objects.get_or_create(enrollment=enrollment)
