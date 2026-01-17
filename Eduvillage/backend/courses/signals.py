from certificates.models import Certificate
from courses.models import Lesson, Progress

def sync_certificate(user, course):
    print("🔵 sync_certificate CALLED")
    print("USER:", user)
    print("COURSE:", course)

    total_lessons = Lesson.objects.filter(course=course).count()
    completed_lessons = Progress.objects.filter(
        student=user,
        lesson__course=course,
        completed=True
    ).count()

    print("TOTAL LESSONS:", total_lessons)
    print("COMPLETED LESSONS:", completed_lessons)

    if total_lessons > 0 and total_lessons == completed_lessons:
        cert, created = Certificate.objects.get_or_create(
            user=user,
            course=course
        )
        print("✅ CERTIFICATE CREATED:", created)
    else:
        Certificate.objects.filter(
            user=user,
            course=course
        ).delete()
        print("❌ CERTIFICATE REMOVED (NOT COMPLETED)")
