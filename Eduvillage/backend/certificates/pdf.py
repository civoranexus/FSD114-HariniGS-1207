from io import BytesIO
import os
import qrcode
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from django.conf import settings


def draw_border(canvas, doc):
    canvas.saveState()
    width, height = landscape(A4)
    margin = 18

    canvas.setStrokeColor(HexColor("#1F3C88"))
    canvas.setLineWidth(4)

    canvas.rect(
        margin,
        margin,
        width - (2 * margin),
        height - (2 * margin),
    )
    canvas.restoreState()


def generate_certificate_pdf(certificate, request=None):
    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=50,
        leftMargin=50,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        fontSize=38,
        alignment=1,
        textColor=HexColor("#1F3C88"),
        spaceAfter=25,
    )

    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        fontSize=18,
        alignment=1,
        spaceAfter=20,
    )

    name_style = ParagraphStyle(
        "NameStyle",
        fontSize=34,
        alignment=1,
        spaceAfter=25,
    )

    course_style = ParagraphStyle(
        "CourseStyle",
        fontSize=26,
        alignment=1,
        spaceAfter=18,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        fontSize=16,
        alignment=1,
        spaceAfter=15,
    )

    footer_style = ParagraphStyle(
        "FooterStyle",
        fontSize=12,
        alignment=1,
        textColor=HexColor("#555555"),
        spaceBefore=20,
    )

    elements = []

    # 🔷 LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        "certificates",
        "static",
        "certificates",
        "civora_logo.png",
    )
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=3 * inch, height=1.2 * inch)
        logo.hAlign = "CENTER"
        elements.append(logo)
        elements.append(Spacer(1, 25))

    # 🔷 TITLE
    elements.append(Paragraph("Certificate of Completion", title_style))

    # 🔷 BODY TEXT
    elements.append(Paragraph("This is proudly presented to", subtitle_style))

    enrollment = certificate.enrollment
    display_name = (
        enrollment.full_name.strip()
        if enrollment.full_name
        else enrollment.user.get_username()
    )
    elements.append(Paragraph(f"<b>{display_name}</b>", name_style))

    elements.append(
        Paragraph("For successfully completing the course", body_style)
    )

    elements.append(
        Paragraph(
            f"<b>{certificate.enrollment.course.title}</b>",
            course_style,
        )
    )

    elements.append(
        Paragraph(
            "Issued by <b>Civora Nexus</b> — empowering future developers.",
            body_style,
        )
    )

    # 🔷 CERTIFICATE ID
    elements.append(
        Paragraph(
            f"Certificate ID: <b>{certificate.verification_code}</b>",
            footer_style,
        )
    )

    # 🔷 SIGNATURE
    elements.append(Spacer(1, 35))
    signature_path = os.path.join(
        settings.BASE_DIR,
        "certificates",
        "static",
        "certificates",
        "signature.png",
    )
    if os.path.exists(signature_path):
        signature = Image(signature_path, width=2.2 * inch, height=0.9 * inch)
        signature.hAlign = "CENTER"
        elements.append(signature)

    elements.append(
        Paragraph(
            "<b>Authorized Signatory</b><br/>CEO, Civora Nexus",
            footer_style,
        )
    )

    # 🔷 QR CODE (BOTTOM RIGHT)
    # Use request to get the proper host (fixes mobile IP restriction)
    if request:
        host = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        verify_url = f"{protocol}://{host}/certificates/verify/{certificate.verification_code}/"
    else:
        # Fallback for direct PDF generation without request
        verify_url = f"http://127.0.0.1:8000/certificates/verify/{certificate.verification_code}/"
    
    qr = qrcode.make(verify_url)
    qr_buffer = BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)

    qr_image = Image(qr_buffer, width=1.3 * inch, height=1.3 * inch)
    qr_image.hAlign = "RIGHT"

    elements.append(Spacer(1, 20))
    elements.append(qr_image)

    pdf.build(elements, onFirstPage=draw_border)
    buffer.seek(0)
    return buffer
