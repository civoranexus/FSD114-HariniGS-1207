import os
from io import BytesIO
from django.conf import settings
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# 🔷 DRAW BORDER FUNCTION
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


# 🔷 CERTIFICATE PDF GENERATOR
def generate_certificate_pdf(user, course):
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
        textColor=HexColor("#000000"),
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
        fontSize=12,
        alignment=1,
        textColor=HexColor("#555555"),
        spaceBefore=20,
    )

    elements = []

    # 🔷 LOGO
    logo_path = os.path.join(
        settings.BASE_DIR,
        "certificates/statics/certificates/civora_logo.png",
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2.5 * inch, height=1 * inch)
        logo.hAlign = "CENTER"
        elements.append(logo)
        elements.append(Spacer(1, 20))

    # 🔷 TITLE
    elements.append(Paragraph("Certificate of Completion", title_style))
    elements.append(Spacer(1, 20))

    # 🔷 BODY CONTENT
    elements.append(Paragraph("This is proudly presented to", subtitle_style))

    elements.append(
        Paragraph(
            f"<b>{user.get_full_name() or user.username}</b>",
            name_style,
        )
    )

    elements.append(
        Paragraph("For successfully completing the course", body_style)
    )

    elements.append(
        Paragraph(f"<b>{course.title}</b>", name_style)
    )

    elements.append(
        Paragraph(
            "Issued by <b>Civora Nexus</b> — empowering future developers.",
            body_style,
        )
    )

    # 🔷 ISSUE DATE
    issued_date = (
        course.updated_at.strftime("%d %B %Y")
        if hasattr(course, "updated_at")
        else ""
    )

    elements.append(
        Paragraph(f"Issued on: {issued_date}", footer_style)
    )

    # 🔷 SIGNATURE SECTION
    elements.append(Spacer(1, 40))

    signature_path = os.path.join(
        settings.BASE_DIR,
        "certificates/statics/certificates/signature.png",
    )

    if os.path.exists(signature_path):
        signature = Image(signature_path, width=2 * inch, height=0.8 * inch)
        signature.hAlign = "CENTER"
        elements.append(signature)

    elements.append(
        Paragraph(
            "<b>Authorized Signatory</b><br/>CEO, Civora Nexus",
            footer_style,
        )
    )

    # 🔷 BUILD PDF WITH BORDER
    pdf.build(
        elements,
        onFirstPage=draw_border,
        onLaterPages=draw_border,
    )

    buffer.seek(0)
    return buffer
