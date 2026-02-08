from django.db import models
from django.conf import settings


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('web-development', 'Web Development'),
        ('mobile-development', 'Mobile Development'),
        ('data-science', 'Data Science'),
        ('artificial-intelligence', 'Artificial Intelligence'),
        ('cloud-computing', 'Cloud Computing'),
        ('cybersecurity', 'Cybersecurity'),
        ('design', 'Design'),
        ('business', 'Business'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_courses"
    )

    class Meta:
        ordering = ['category', 'title']

    def __str__(self):
        return self.title



class Lesson(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    course = models.ForeignKey(
        Course,
        related_name="lessons",
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to="lesson_videos/", blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=Course.CATEGORY_CHOICES,
        default='other'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner'
    )

    order = models.PositiveIntegerField(default=0)  # drag & drop
    is_active = models.BooleanField(default=True)   # soft delete

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']  # IMPORTANT for lesson flow

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    
class LessonCompletion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user} completed {self.lesson.title}"


class Enrollment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user} - {self.course}"



class Progress(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="progress"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("enrollment", "lesson")

    def __str__(self):
        return f"{self.enrollment.user} - {self.lesson.title}"

