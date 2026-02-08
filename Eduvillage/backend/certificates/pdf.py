from io import BytesIO
import os
import qrcode
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from django.conf import settings


def draw_border_and_qr(canvas_obj, doc, qr_image_buffer):
    """Draw professional certificate border and QR code in bottom right"""
    canvas_obj.saveState()
    width, height = landscape(A4)
    margin = 22

    # Main border with Civora brand colors
    canvas_obj.setStrokeColor(HexColor("#1B9AAA"))
    canvas_obj.setLineWidth(3)
    canvas_obj.rect(
        margin,
        margin,
        width - (2 * margin),
        height - (2 * margin),
    )
    
    # Inner accent border
    canvas_obj.setStrokeColor(HexColor("#142C52"))
    canvas_obj.setLineWidth(1)
    canvas_obj.rect(
        margin + 4,
        margin + 4,
        width - (2 * margin) - 8,
        height - (2 * margin) - 8,
    )

    # Draw QR code in bottom right corner
    if qr_image_buffer:
        qr_img = Image(qr_image_buffer, width=1 * inch, height=1 * inch)
        qr_img.drawOn(canvas_obj, width - margin - 1.2 * inch, margin + 0.3 * inch)
    
    canvas_obj.restoreState()


def generate_certificate_pdf(certificate, request=None):
    """Generate professional Civora Nexus certificate PDF"""
    
    # Generate QR code first
    if request:
        host = request.get_host()
        protocol = 'https' if request.is_secure() else 'http'
        verify_url = f"{protocol}://{host}/certificates/verify/{certificate.verification_code}/"
    else:
        verify_url = f"http://127.0.0.1:8000/certificates/verify/{certificate.verification_code}/"
    
    qr = qrcode.make(verify_url)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    buffer = BytesIO()

    # Create a custom callback that includes the QR code
    def draw_page(canvas_obj, doc):
        draw_border_and_qr(canvas_obj, doc, qr_buffer)

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=60,
        leftMargin=60,
        topMargin=50,
        bottomMargin=50,
    )

    styles = getSampleStyleSheet()

    # Professional title style with Civora colors
    title_style = ParagraphStyle(
        "TitleStyle",
        fontSize=44,
        alignment=1,
        textColor=HexColor("#1B9AAA"),
        spaceAfter=4,
        fontName="Helvetica-Bold",
        leading=46,
    )

    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        fontSize=13,
        alignment=1,
        textColor=HexColor("#666666"),
        spaceAfter=22,
        fontName="Helvetica",
        leading=15,
    )

    # Student name style
    name_style = ParagraphStyle(
        "NameStyle",
        fontSize=36,
        alignment=1,
        textColor=HexColor("#1B9AAA"),
        spaceAfter=10,
        fontName="Helvetica-Bold",
        leading=40,
    )

    # Course name style
    course_style = ParagraphStyle(
        "CourseStyle",
        fontSize=28,
        alignment=1,
        textColor=HexColor("#1F3C88"),
        spaceAfter=16,
        fontName="Helvetica-Bold",
        leading=32,
    )

    # Body text style
    body_style = ParagraphStyle(
        "BodyStyle",
        fontSize=12,
        alignment=1,
        textColor=HexColor("#444444"),
        spaceAfter=8,
        fontName="Helvetica",
        leading=14,
    )

    # Footer/ID style
    footer_style = ParagraphStyle(
        "FooterStyle",
        fontSize=10,
        alignment=1,
        textColor=HexColor("#888888"),
        spaceBefore=10,
        spaceAfter=6,
        fontName="Helvetica",
        leading=11,
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
        logo = Image(logo_path, width=2.8 * inch, height=1 * inch)
        logo.hAlign = "CENTER"
        elements.append(logo)
        elements.append(Spacer(1, 12))
    else:
        elements.append(Spacer(1, 8))

    # 🔷 TITLE
    elements.append(Paragraph("Certificate of Completion", title_style))

    # 🔷 SUBTITLE
    elements.append(Paragraph("This is proudly presented to", subtitle_style))

    # 🔷 STUDENT NAME
    enrollment = certificate.enrollment
    display_name = (
        enrollment.full_name.strip()
        if enrollment.full_name
        else enrollment.user.get_username()
    )
    elements.append(Paragraph(display_name, name_style))

    # 🔷 COURSE TEXT
    elements.append(Paragraph("For successfully completing the course", body_style))
    
    # 🔷 COURSE NAME
    elements.append(
        Paragraph(
            certificate.enrollment.course.title,
            course_style,
        )
    )

    # 🔷 ISSUER TEXT
    elements.append(Spacer(1, 6))
    elements.append(
        Paragraph(
            "Issued by <b>Civora Nexus</b> — empowering future developers.",
            body_style,
        )
    )

    # 🔷 CERTIFICATE ID
    elements.append(Spacer(1, 12))
    elements.append(
        Paragraph(
            f"Certificate ID: {certificate.verification_code}",
            footer_style,
        )
    )

    # 🔷 SIGNATURE SECTION
    elements.append(Spacer(1, 18))
    
    signature_path = os.path.join(
        settings.BASE_DIR,
        "certificates",
        "static",
        "certificates",
        "signature.png",
    )
    if os.path.exists(signature_path):
        signature = Image(signature_path, width=1.6 * inch, height=0.6 * inch)
        signature.hAlign = "CENTER"
        elements.append(signature)
    
    elements.append(Spacer(1, 4))
    elements.append(
        Paragraph(
            "Authorized Signatory<br/><b>CEO, Civora Nexus</b>",
            footer_style,
        )
    )

    pdf.build(elements, onFirstPage=draw_page)
    buffer.seek(0)
    return buffer
