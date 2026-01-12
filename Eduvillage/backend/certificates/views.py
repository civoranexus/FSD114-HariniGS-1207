from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from courses.models import Course
from .pdf import generate_certificate_pdf

@login_required
def download_certificate(request, course_id):
    """
    Generate and return the PDF certificate for a course.
    """
    # Get the course object
    course = get_object_or_404(Course, id=course_id)

    # Generate the PDF
    pdf_buffer = generate_certificate_pdf(request.user, course)

    # Return as downloadable file
    response = HttpResponse(pdf_buffer, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="{course.title}_certificate.pdf"'
    return response



