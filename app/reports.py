import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from app import models


def build_pdf(user: models.User, role: models.Role, a: models.Assessment) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleBig", parent=styles["Title"], textColor=colors.HexColor("#4338CA"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#1E1B4B"))
    body = styles["BodyText"]

    story = [
        Paragraph("SkillSense AI — Performance Report", title_style),
        Spacer(1, 6),
        Paragraph(f"{user.name} &nbsp;|&nbsp; {role.name} &nbsp;|&nbsp; {datetime.utcnow().strftime('%d %b %Y')}", body),
        Spacer(1, 18),
        Paragraph(f"Overall skill score: {a.overall_score}%", h2),
        Paragraph(f"Career readiness: {a.readiness['label']} (threshold {a.readiness['threshold']}%)", body),
        Paragraph(a.readiness["note"], body),
        Spacer(1, 14),
        Paragraph("Skill breakdown", h2),
    ]

    skill_rows = [["Topic", "Score"]] + [[s["name"], f"{s['score']}%"] for s in a.skills]
    skill_table = Table(skill_rows, colWidths=[8 * cm, 3 * cm])
    skill_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366F1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E4E0FA")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F5FF")]),
    ]))
    story += [skill_table, Spacer(1, 16)]

    story.append(Paragraph("Strengths", h2))
    for s in a.strengths:
        story.append(Paragraph(f"• <b>{s['topic']}</b> — {s['detail']}", body))
    if not a.strengths:
        story.append(Paragraph("No standout strengths yet — keep practicing.", body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Knowledge gaps", h2))
    for g in a.gaps:
        story.append(Paragraph(f"• <b>{g['topic']}</b> ({g['severity']}) — {g['pattern']}", body))
    if not a.gaps:
        story.append(Paragraph("No significant gaps detected this round.", body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Recommendation", h2))
    story.append(Paragraph(f"<b>{a.recommendation['headline']}</b>", body))
    story.append(Paragraph(a.recommendation["detail"], body))
    for act in a.recommendation["actions"]:
        story.append(Paragraph(f"• {act}", body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Learning roadmap", h2))
    for phase in a.roadmap:
        story.append(Paragraph(f"<b>{phase['window']}</b>", body))
        for goal in phase["goals"]:
            story.append(Paragraph(f"– {goal}", body))

    doc.build(story)
    buf.seek(0)
    return buf


def build_excel(role: models.Role, a: models.Assessment) -> io.BytesIO:
    wb = Workbook()

    ws = wb.active
    ws.title = "Skill Matrix"
    header_fill = PatternFill(start_color="6366F1", end_color="6366F1", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)

    ws.append(["Topic", "Score (%)"])
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
    for s in a.skills:
        ws.append([s["name"], s["score"]])
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 12

    ws2 = wb.create_sheet("Gaps & Strengths")
    ws2.append(["Type", "Topic", "Detail / Pattern", "Severity"])
    for cell in ws2[1]:
        cell.fill = header_fill
        cell.font = header_font
    for s in a.strengths:
        ws2.append(["Strength", s["topic"], s["detail"], ""])
    for g in a.gaps:
        ws2.append(["Gap", g["topic"], g["pattern"], g["severity"]])
    for col, width in zip("ABCD", (12, 20, 50, 12)):
        ws2.column_dimensions[col].width = width

    ws3 = wb.create_sheet("Summary")
    ws3.append(["Role", role.name])
    ws3.append(["Overall score", a.overall_score])
    ws3.append(["Readiness label", a.readiness["label"]])
    ws3.append(["Readiness threshold", a.readiness["threshold"]])
    ws3.column_dimensions["A"].width = 20
    ws3.column_dimensions["B"].width = 30

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
