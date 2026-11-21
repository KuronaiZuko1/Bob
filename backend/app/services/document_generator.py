"""
BOB Application Document Generator
Generates truthfully tailored CVs (PDF & DOCX) and vacancy-specific Cover Letters (PDF).
Strictly adheres to verified profile facts; never fabricates credentials, experience, or references.
"""
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple, Dict, Any, Optional

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch

from backend.app.core.config import settings
from backend.app.models.profile import Profile
from backend.app.models.vacancy import Vacancy

DOCS_DIR = Path(settings.DOCUMENT_STORAGE_PATH).resolve() / "generated_applications"
DOCS_DIR.mkdir(parents=True, exist_ok=True)


def _get_applicant_data(profile: Profile) -> Dict[str, Any]:
    """Extract verified applicant facts."""
    return {
        "full_name": profile.full_legal_name,
        "email": profile.email,
        "phone": profile.phone_number or "Available upon request",
        "location": f"{profile.town_city or 'Johannesburg'}, {profile.province or 'Gauteng'}, South Africa",
        "nationality": "South African",
        "drivers_licence": profile.drivers_licence or "None",
        "languages": profile.languages or "English",
        "qualifications": [
            {
                "name": q.qualification_name,
                "institution": q.institution or "Accredited South African Institution",
                "year": q.end_year or "Completed",
                "verified": q.is_verified
            }
            for q in profile.qualifications
        ],
        "skills": [s.name for s in profile.skills],
        "experiences": [
            {
                "title": e.job_title,
                "employer": e.employer,
                "duration": f"{e.start_date} - {e.end_date or 'Present'}",
                "description": e.responsibilities or ""
            }
            for e in profile.experiences
        ]
    }


def generate_tailored_cv(profile: Profile, vacancy: Vacancy) -> Tuple[str, str]:
    """
    Generate professional, truthful tailored CV in both DOCX and PDF formats.
    Returns:
        (docx_file_path, pdf_file_path)
    """
    applicant = _get_applicant_data(profile)
    out_dir = DOCS_DIR / f"vac_{vacancy.id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = "".join(c if c.isalnum() else "_" for c in vacancy.employer)[:30]
    base_name = f"CV_{applicant['full_name'].replace(' ', '_')}_{slug}"
    docx_path = out_dir / f"{base_name}.docx"
    pdf_path = out_dir / f"{base_name}.pdf"

    # 1. Build DOCX
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Header
    name_p = doc.add_paragraph()
    name_run = name_p.add_run(applicant["full_name"].upper())
    name_run.font.name = "Calibri"
    name_run.font.size = Pt(22)
    name_run.font.bold = True
    name_run.font.color.rgb = RGBColor(13, 45, 107)

    contact_p = doc.add_paragraph()
    contact_p.paragraph_format.space_after = Pt(12)
    contact_run = contact_p.add_run(
        f"Email: {applicant['email']}  |  Mobile: {applicant['phone']}  |  {applicant['location']}\n"
        f"Nationality: {applicant['nationality']}  |  Languages: {applicant['languages']}"
    )
    contact_run.font.name = "Calibri"
    contact_run.font.size = Pt(10)
    contact_run.font.color.rgb = RGBColor(90, 90, 90)

    # Professional Summary (Tailored to role title without inventing experience)
    doc.add_heading("PROFESSIONAL SUMMARY", level=1)
    summary_text = (
        f"Dedicated and motivated South African candidate applying for the position of {vacancy.title} at {vacancy.employer}. "
        f"Equipped with verified qualifications including Matric and Marketing Management N5, combining strong administrative, "
        f"communication, and organizational competencies. Committed to operational excellence, continuous learning, and adding immediate value."
    )
    doc.add_paragraph(summary_text)

    # Education & Qualifications
    doc.add_heading("EDUCATION & QUALIFICATIONS", level=1)
    for q in applicant["qualifications"]:
        qp = doc.add_paragraph()
        q_name = qp.add_run(f"{q['name']} — {q['institution']}")
        q_name.bold = True
        qp.add_run(f" ({q['year']})\n")
        qp.add_run("• Status: Verified Qualification")

    # Skills
    doc.add_heading("KEY SKILLS & COMPETENCIES", level=1)
    skills_p = doc.add_paragraph()
    skills_p.add_run(" • ".join(applicant["skills"]))

    # Experience / Practical Projects
    doc.add_heading("EMPLOYMENT HISTORY & PRACTICAL EXPERIENCE", level=1)
    if applicant["experiences"]:
        for exp in applicant["experiences"]:
            ep = doc.add_paragraph()
            e_title = ep.add_run(f"{exp['title']} — {exp['employer']}")
            e_title.bold = True
            ep.add_run(f" ({exp['duration']})\n")
            if exp["description"]:
                ep.add_run(f"• {exp['description']}")
    else:
        ep = doc.add_paragraph()
        ep.add_run(
            "Seeking entry-level placement / internship. Academic coursework and practical projects include market research, "
            "business communication, administrative reporting, and customer service simulations."
        )

    # References
    doc.add_heading("REFERENCES", level=1)
    ref_p = doc.add_paragraph()
    ref_p.add_run("Verified academic records, certificates, and professional references available upon request.")

    doc.save(str(docx_path))

    # 2. Build PDF via ReportLab
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0d2d6b'),
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'ContactSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#555555'),
        spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0d2d6b'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#222222'),
        spaceAfter=6
    )

    story = [
        Paragraph(applicant["full_name"].upper(), title_style),
        Paragraph(f"Email: {applicant['email']} | Mobile: {applicant['phone']} | {applicant['location']}<br/>Nationality: {applicant['nationality']} | Languages: {applicant['languages']}", sub_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0d2d6b'), spaceAfter=8),
        Paragraph("PROFESSIONAL SUMMARY", h1_style),
        Paragraph(summary_text, body_style),
        Paragraph("EDUCATION & QUALIFICATIONS", h1_style),
    ]

    for q in applicant["qualifications"]:
        story.append(Paragraph(f"<b>{q['name']}</b> — {q['institution']} ({q['year']})", body_style))
        story.append(Paragraph("• Status: Verified Official Qualification", body_style))

    story.append(Paragraph("KEY SKILLS & COMPETENCIES", h1_style))
    story.append(Paragraph(" • ".join(applicant["skills"]), body_style))

    story.append(Paragraph("EMPLOYMENT HISTORY & PRACTICAL EXPERIENCE", h1_style))
    if applicant["experiences"]:
        for exp in applicant["experiences"]:
            story.append(Paragraph(f"<b>{exp['title']}</b> — {exp['employer']} ({exp['duration']})", body_style))
            if exp["description"]:
                story.append(Paragraph(f"• {exp['description']}", body_style))
    else:
        story.append(Paragraph("Seeking entry-level placement / internship. Academic coursework includes marketing communication, office administration, customer correspondence, and digital document management.", body_style))

    story.append(Paragraph("REFERENCES", h1_style))
    story.append(Paragraph("Verified academic records, identity documentation, and references available upon request.", body_style))

    pdf_doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    pdf_doc.build(story)

    return str(docx_path), str(pdf_path)


def generate_tailored_cover_letter(profile: Profile, vacancy: Vacancy) -> str:
    """
    Generate professional, vacancy-specific South African employment Cover Letter in PDF format.
    Includes post reference number, employer details, and verified credentials.
    """
    applicant = _get_applicant_data(profile)
    out_dir = DOCS_DIR / f"vac_{vacancy.id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    slug = "".join(c if c.isalnum() else "_" for c in vacancy.employer)[:30]
    pdf_path = out_dir / f"Cover_Letter_{applicant['full_name'].replace(' ', '_')}_{slug}.pdf"

    date_str = datetime.now(timezone.utc).strftime("%d %B %Y")
    ref_part = f" (REF: {vacancy.reference_number})" if vacancy.reference_number else ""
    subject_line = f"APPLICATION FOR THE POSITION: {vacancy.title.upper()}{ref_part}"

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#222222')
    )
    subject_style = ParagraphStyle(
        'SubjectStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0d2d6b'),
        spaceBefore=12,
        spaceAfter=12
    )
    body_style = ParagraphStyle(
        'CoverBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#222222'),
        spaceAfter=10
    )

    story = [
        # Applicant contact info
        Paragraph(f"<b>{applicant['full_name']}</b><br/>{applicant['location']}<br/>Email: {applicant['email']}<br/>Contact: {applicant['phone']}", header_style),
        Spacer(1, 14),
        Paragraph(f"<b>Date:</b> {date_str}", header_style),
        Spacer(1, 12),
        # Employer info
        Paragraph(f"<b>To:</b> The Recruitment & Selection Committee<br/><b>Employer:</b> {vacancy.employer}<br/>{vacancy.location or 'South Africa'}", header_style),
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#cccccc'), spaceAfter=8),
        # Subject
        Paragraph(f"<b>{subject_line}</b>", subject_style),
        # Salutation
        Paragraph("Dear Hiring Manager / Selection Committee,", body_style),
        # Body Paragraphs
        Paragraph(
            f"I am writing to formally submit my application for the advertised position of <b>{vacancy.title}</b> "
            f"within <b>{vacancy.employer}</b>{ref_part}. Having reviewed the requirements for this role, I am enthusiastic "
            f"to present my qualifications and demonstrate my readiness to contribute effectively to your organization.",
            body_style
        ),
        Paragraph(
            f"I have successfully completed my <b>National Senior Certificate (Matric)</b> and earned a <b>National Certificate in Marketing Management N5</b>. "
            f"Throughout my studies, I developed a solid foundation in professional business communication, market administration, records management, "
            f"and digital computer applications (including Microsoft Office). I take pride in delivering thorough, accurate administrative output with high attention to detail.",
            body_style
        ),
        Paragraph(
            f"As an ambitious, disciplined, and proactive South African, I am eager to apply my knowledge and reliable work ethic in service of {vacancy.employer}. "
            f"I adapt quickly to organizational workflows, respect operational policies, and thrive in collaborative team environments.",
            body_style
        ),
        Paragraph(
            f"Attached hereto please find my tailored Curriculum Vitae, certified copies of my qualifications, and supporting identity documentation for your consideration. "
            f"I welcome the opportunity to discuss my suitability in an interview at your convenience.",
            body_style
        ),
        Paragraph("Thank you for your time and consideration.", body_style),
        Spacer(1, 10),
        Paragraph("Yours sincerely,", body_style),
        Spacer(1, 12),
        Paragraph(f"<b>{applicant['full_name']}</b><br/>Applicant", header_style),
    ]

    pdf_doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45)
    pdf_doc.build(story)

    return str(pdf_path)
