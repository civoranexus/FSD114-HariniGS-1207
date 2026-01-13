import uuid
from django.db import models
from django.conf import settings
from courses.models import Course
from courses.models import Enrollment


class Certificate(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    enrollment = models.OneToOneField(
        "courses.Enrollment",
        on_delete=models.CASCADE,
        related_name="certificate"
    )

    certificate_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True   # ✅ allow empty before save()
    )

    issuer = models.CharField(
        max_length=255,
        default="Civora Nexus"
    )

    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = f"CVN-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificate - {self.student} - {self.course}"


