from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='teaching_courses',
        limit_choices_to={'role': 'teacher'}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = (
        ('video', 'Video'),
        ('text', 'Text'),
        ('pdf', 'PDF'),
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES
    )
    content = models.TextField(help_text="URL or text content")
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.full_name} enrolled in {self.course.title}"



class Progress(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'lesson')




