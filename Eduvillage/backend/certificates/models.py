import uuid
from django.db import models
from courses.models import Enrollment

class Certificate(models.Model):
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="certificate"
    )

    verification_code = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )

    issued_at = models.DateTimeField(auto_now_add=True)
    verification_code = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )
    downloaded = models.BooleanField(default=False)
    revoked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = f"CVN-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificate - {self.enrollment.full_name}"
