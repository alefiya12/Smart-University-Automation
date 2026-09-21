"""
services/pdf_service.py — ReportLab PDF generators for admission letters and marksheets.
"""
import os
import logging
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)

BLUE   = colors.HexColor('#1A56DB')
BLACK  = colors.HexColor('#111827')
GREY   = colors.HexColor('#6B7280')
LIGHT  = colors.HexColor('#F8F9FA')
BORDER = colors.HexColor('#E5E7EB')

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'reports', 'pdfs')


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


# ─── Admission Letter ──────────────────────────────────────────────────────────
def generate_admission_letter(
    enrollment_no: str,
    student_name: str,
    email: str,
    department: str,
    course: str,
    semester: int,
    admission_year: int,
    temp_password: str,
) -> str:
    """
    Generate an admission letter PDF.
    Returns the absolute path to the generated file.
    """
    _ensure_dir(REPORTS_DIR)
    filename = f"admission_{enrollment_no}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
    )

    styles = getSampleStyleSheet()
    title_style  = ParagraphStyle('title',  fontName='Helvetica-Bold', fontSize=18, textColor=BLUE,  alignment=TA_CENTER, spaceAfter=4)
    sub_style    = ParagraphStyle('sub',    fontName='Helvetica',      fontSize=10, textColor=GREY,  alignment=TA_CENTER, spaceAfter=20)
    heading_style= ParagraphStyle('h2',     fontName='Helvetica-Bold', fontSize=12, textColor=BLACK, spaceAfter=6)
    body_style   = ParagraphStyle('body',   fontName='Helvetica',      fontSize=10, textColor=BLACK, leading=16, spaceAfter=8)
    small_style  = ParagraphStyle('small',  fontName='Helvetica',      fontSize=9,  textColor=GREY,  spaceAfter=4)

    story = []

    # Header
    story.append(Paragraph("SMART UNIVERSITY", title_style))
    story.append(Paragraph("Admission Confirmation Letter", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=20))

    # Date
    story.append(Paragraph(f"Date: {datetime.utcnow().strftime('%d %B %Y')}", small_style))
    story.append(Spacer(1, 0.3*cm))

    # Greeting
    story.append(Paragraph(f"Dear {student_name},", body_style))
    story.append(Paragraph(
        "We are pleased to inform you that your application for admission to Smart University "
        "has been successfully processed. Congratulations on your admission!",
        body_style,
    ))
    story.append(Spacer(1, 0.4*cm))

    # Details table
    story.append(Paragraph("Admission Details", heading_style))
    details = [
        ["Enrollment Number", enrollment_no],
        ["Student Name",      student_name],
        ["Email Address",     email],
        ["Department",        department],
        ["Course",            course],
        ["Semester",          str(semester)],
        ["Admission Year",    str(admission_year)],
        ["Temporary Password",temp_password],
    ]
    tbl = Table(details, colWidths=[5*cm, 10*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (0, -1), LIGHT),
        ('TEXTCOLOR',   (0, 0), (0, -1), GREY),
        ('TEXTCOLOR',   (1, 0), (1, -1), BLACK),
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',    (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE',    (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, LIGHT]),
        ('GRID',        (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING',     (0, 0), (-1, -1), 8),
        ('BACKGROUND',  (1, 7), (1, 7), colors.HexColor('#EBF1FF')),  # highlight temp password
        ('TEXTCOLOR',   (1, 7), (1, 7), BLUE),
        ('FONTNAME',    (1, 7), (1, 7), 'Helvetica-Bold'),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.6*cm))

    # Instructions
    story.append(Paragraph("Important Instructions", heading_style))
    story.append(Paragraph(
        "1. Login to the student portal using your enrollment number and the temporary password shown above.<br/>"
        "2. Change your password immediately after your first login.<br/>"
        "3. Keep your enrollment number safe — it is required for all university transactions.<br/>"
        "4. Contact the admission office if you face any issues.",
        body_style,
    ))

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph("Registrar, Smart University", small_style))
    story.append(Paragraph(
        f"This is a system-generated letter. Generated on {datetime.utcnow().strftime('%d %B %Y at %H:%M UTC')}",
        small_style,
    ))

    doc.build(story)
    logger.info("Admission letter generated: %s", filepath)
    return filepath


# ─── Marksheet PDF ────────────────────────────────────────────────────────────
def generate_marksheet(
    enrollment_no: str,
    student_name: str,
    department: str,
    course: str,
    semester: int,
    academic_year: str,
    results: list,   # list of dicts: subject, credits, marks, max_marks, grade, grade_points
    sgpa: float,
    cgpa: float,
) -> str:
    """
    Generate a semester marksheet PDF.
    Returns absolute file path.
    """
    _ensure_dir(REPORTS_DIR)
    filename = f"marksheet_{enrollment_no}_sem{semester}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2.5*cm, rightMargin=2.5*cm)
    styles = getSampleStyleSheet()
    title_style  = ParagraphStyle('t',  fontName='Helvetica-Bold', fontSize=16, textColor=BLUE, alignment=TA_CENTER, spaceAfter=4)
    sub_style    = ParagraphStyle('s',  fontName='Helvetica',      fontSize=10, textColor=GREY, alignment=TA_CENTER, spaceAfter=16)
    heading_style= ParagraphStyle('h',  fontName='Helvetica-Bold', fontSize=11, textColor=BLACK, spaceAfter=6)
    small_style  = ParagraphStyle('sm', fontName='Helvetica',      fontSize=9,  textColor=GREY, spaceAfter=4)

    story = []
    story.append(Paragraph("SMART UNIVERSITY", title_style))
    story.append(Paragraph(f"Semester {semester} Marksheet — {academic_year}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=16))

    # Student info
    info_data = [
        [Paragraph('<b>Enrollment No.</b>', styles['Normal']), enrollment_no,
         Paragraph('<b>Name</b>', styles['Normal']),            student_name],
        [Paragraph('<b>Department</b>', styles['Normal']),      department,
         Paragraph('<b>Course</b>', styles['Normal']),           course],
    ]
    info_tbl = Table(info_data, colWidths=[3.5*cm, 5.5*cm, 2.5*cm, 5*cm])
    info_tbl.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN',   (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID',     (0, 0), (-1, -1), 0.5, BORDER),
        ('PADDING',  (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), LIGHT),
        ('BACKGROUND', (2, 0), (2, -1), LIGHT),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 0.5*cm))

    # Results table
    story.append(Paragraph("Subject-wise Results (Dual-Threshold Evaluation)", heading_style))
    header = ['Subject', 'Credits', 'Internal\n(Max 30)', 'External\n(Max 70)', 'Total\n(Max 100)', 'Grade', 'Status']
    rows = [header]
    for r in results:
        pass_status = r.get('pass_status', True)
        status_text = 'PASS' if pass_status else 'FAIL'
        rows.append([
            r.get('subject', '') or r.get('subject_name', ''),
            str(r.get('credits', 4)),
            f"{float(r.get('internal_score', r.get('marks', 0))):.1f}",
            f"{float(r.get('external_score', 0)):.1f}",
            f"{float(r.get('total_marks_obtained', r.get('marks', 0))):.1f}",
            str(r.get('grade_letter', r.get('grade', ''))),
            status_text,
        ])

    res_tbl = Table(rows, colWidths=[4.5*cm, 1.8*cm, 2.3*cm, 2.3*cm, 2.3*cm, 1.8*cm, 2*cm])
    res_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
        ('GRID',       (0, 0), (-1, -1), 0.5, BORDER),
        ('ALIGN',      (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING',    (0, 0), (-1, -1), 6),
    ]))
    story.append(res_tbl)
    story.append(Spacer(1, 0.5*cm))

    # SGPA / CGPA summary
    summary_data = [['SGPA', f'{sgpa:.2f}', 'CGPA', f'{cgpa:.2f}']]
    sum_tbl = Table(summary_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
    sum_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EBF1FF')),
        ('TEXTCOLOR',  (0, 0), (0, -1), GREY),
        ('TEXTCOLOR',  (2, 0), (2, -1), GREY),
        ('FONTNAME',   (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME',   (3, 0), (3, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR',  (1, 0), (1, -1), BLUE),
        ('TEXTCOLOR',  (3, 0), (3, -1), BLUE),
        ('FONTSIZE',   (0, 0), (-1, -1), 11),
        ('ALIGN',      (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',     (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID',       (0, 0), (-1, -1), 0.5, BORDER),
        ('PADDING',    (0, 0), (-1, -1), 10),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"Generated on {datetime.utcnow().strftime('%d %B %Y')} | Smart University", small_style))

    doc.build(story)
    logger.info("Marksheet generated: %s", filepath)
    return filepath
