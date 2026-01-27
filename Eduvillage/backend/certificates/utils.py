from courses.models import Enrollment, Lesson, Progress
from certificates.models import Certificate
import qrcode
from io import BytesIO
import base64

def sync_certificate(user, course):
    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
    except Enrollment.DoesNotExist:
        return

    total_lessons = Lesson.objects.filter(course=course).count()
    completed_lessons = Progress.objects.filter(
        enrollment=enrollment,
        completed=True
    ).count()

    if total_lessons == completed_lessons and total_lessons > 0:
        Certificate.objects.get_or_create(enrollment=enrollment)


def generate_qr_code_base64(data):
    """
    Generate QR code as base64 data URI for HTML img tag.
    
    Args:
        data: String to encode in QR code
    
    Returns:
        Base64 data URI string for use in <img src="data:...">
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert PIL image to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"
