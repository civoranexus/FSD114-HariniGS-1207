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

    margin = 20
    canvas.setStrokeColor(HexColor("#1F3C88"))
    canvas.setLineWidth(4)

    canvas.rect(
        margin,
        margin,
        width - (2 * margin),
        height - (2 * margin),
    )

    canvas.restoreState()


def generate_certificate_pdf(certificate):
    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        fontSize=34,
        alignment=1,
        textColor=HexColor("#1F3C88"),
        spaceAfter=20,
    )
    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        fontSize=16,
        alignment=1,
        spaceAfter=30,
    )
    name_style = ParagraphStyle(
        "NameStyle",
        fontSize=26,
        alignment=1,
        spaceAfter=20,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        fontSize=14,
        alignment=1,
        spaceAfter=20,
    )
    footer_style = ParagraphStyle(
        "FooterStyle",
        fontSize=11,
        alignment=1,
        textColor=HexColor("#555555"),
        spaceBefore=15,
    )

    # ✅ SAFE STUDENT NAME
    enrollment = certificate.enrollment
    display_name = (
        enrollment.full_name.strip()
        if enrollment.full_name
        else enrollment.user.get_username()
    )

    elements = []

    # 🔷 LOGO (FIXED PATH)
    logo_path = os.path.join(
        settings.BASE_DIR,
        "certificates",
        "static",
        "certificates",
        "civora_logo.png",
    )
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2.5 * inch, height=1 * inch)
        logo.hAlign = "CENTER"
        elements.append(logo)
        elements.append(Spacer(1, 20))

    # 🔷 TITLE
    elements.append(Paragraph("Certificate of Completion", title_style))
    elements.append(Spacer(1, 20))

    # 🔷 BODY
    elements.append(Paragraph("This is proudly presented to", subtitle_style))
    elements.append(Paragraph(f"<b>{display_name}</b>", name_style))
    elements.append(Paragraph("For successfully completing the course", body_style))
    elements.append(
        Paragraph(
            f"<b>{certificate.enrollment.course.title}</b>",
            name_style,
        )
    )
    elements.append(
        Paragraph(
            "Issued by <b>Civora Nexus</b> — empowering future developers.",
            body_style,
        )
    )

    # 🔷 CERTIFICATE ID (FIXED)
    elements.append(
        Paragraph(
            f"Certificate ID: <b>{certificate.verification_code}</b>",
            footer_style,
        )
    )

    # 🔷 SIGNATURE
    elements.append(Spacer(1, 30))
    signature_path = os.path.join(
        settings.BASE_DIR,
        "certificates",
        "static",
        "certificates",
        "signature.png",
    )
    if os.path.exists(signature_path):
        signature = Image(signature_path, width=2 * inch, height=0.8 * inch)
        signature.hAlign = "CENTER"
        elements.append(signature)

    elements.append(
        Paragraph("<b>Authorized Signatory</b><br/>CEO, Civora Nexus", footer_style)
    )

    # 🔷 QR CODE
    verify_url = (
        f"http://127.0.0.1:8000/"
        f"certificates/verify/{certificate.verification_code}/"
    )
    qr = qrcode.make(verify_url)
    qr_buffer = BytesIO()
    qr.save(qr_buffer)
    qr_buffer.seek(0)

    qr_image = Image(qr_buffer, width=1.2 * inch, height=1.2 * inch)
    qr_image.hAlign = "RIGHT"

    elements.append(Spacer(1, 20))
    elements.append(qr_image)
    elements.append(
        Paragraph("Scan to verify certificate authenticity", footer_style)
    )

    pdf.build(elements, onFirstPage=draw_border, onLaterPages=draw_border)

    buffer.seek(0)
    return buffer
