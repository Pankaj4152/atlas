"""
PDF Report Generator for Atlas Server Log Analyzer.
Uses ReportLab to generate clean, professional SRE incident reports.
"""

from io import BytesIO
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)


def generate_pdf_report(report_data: Dict[str, Any]) -> BytesIO:
    """
    Generate an executive PDF incident summary from analysis report JSON.
    Returns a BytesIO buffer ready for streaming.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    bold_label = ParagraphStyle(
        "BoldLabel",
        parent=body_style,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0f172a"),
    )

    elements = []

    # 1. Header
    file_info = report_data.get("file_info", {})
    summary = report_data.get("summary", {})
    fname = file_info.get("file_name", "server.log")
    analyzed_at = file_info.get("analyzed_at", "")[:19].replace("T", " ")

    elements.append(Paragraph("AI-Powered Server Anomaly Analysis Report", title_style))
    elements.append(
        Paragraph(
            f"Analyzed File: <b>{fname}</b> | Timestamp: {analyzed_at} | Duration: {file_info.get('duration_seconds', 0)}s",
            subtitle_style,
        )
    )
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

    # 2. Executive Metrics Summary Table
    elements.append(Paragraph("Executive Summary", h2_style))
    summary_table_data = [
        [
            Paragraph("<b>Total Logs Analyzed</b>", bold_label),
            Paragraph(str(summary.get("total_logs", 0)), body_style),
            Paragraph("<b>Analyzed Windows</b>", bold_label),
            Paragraph(str(summary.get("total_windows", 0)), body_style),
        ],
        [
            Paragraph("<b>Flagged Anomalies</b>", bold_label),
            Paragraph(str(summary.get("flagged_windows", 0)), body_style),
            Paragraph("<b>Critical Incidents</b>", bold_label),
            Paragraph(f"<font color='#dc2626'><b>{summary.get('critical_incidents', 0)}</b></font>", body_style),
        ],
    ]
    t = Table(summary_table_data, colWidths=[1.8 * inch, 1.4 * inch, 1.8 * inch, 1.4 * inch])
    t.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    elements.append(t)
    elements.append(Spacer(1, 14))

    # 3. Log Severity Distribution
    sev_dist = summary.get("severity_distribution", {})
    elements.append(Paragraph("Log Severity Breakdown", h2_style))
    sev_data = [
        ["Severity Level", "Count", "% of Total"],
        ["CRITICAL", str(sev_dist.get("CRITICAL", 0)), f"{(sev_dist.get('CRITICAL', 0) / max(summary.get('total_logs', 1), 1)):.1%}"],
        ["ERROR", str(sev_dist.get("ERROR", 0)), f"{(sev_dist.get('ERROR', 0) / max(summary.get('total_logs', 1), 1)):.1%}"],
        ["WARNING", str(sev_dist.get("WARNING", 0)), f"{(sev_dist.get('WARNING', 0) / max(summary.get('total_logs', 1), 1)):.1%}"],
        ["INFO", str(sev_dist.get("INFO", 0)), f"{(sev_dist.get('INFO', 0) / max(summary.get('total_logs', 1), 1)):.1%}"],
    ]
    st = Table(sev_data, colWidths=[2.5 * inch, 2.0 * inch, 2.0 * inch])
    st.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ])
    )
    elements.append(st)
    elements.append(Spacer(1, 14))

    # 4. Detected Incidents & Root Causes
    incidents = report_data.get("incidents", [])
    elements.append(Paragraph(f"Detected Incidents & AI Root-Cause Analysis ({len(incidents)})", h2_style))

    if not incidents:
        elements.append(Paragraph("<i>No critical anomalies or system failures detected.</i>", body_style))
    else:
        for idx, inc in enumerate(incidents, 1):
            inc_elements = []
            sev_badge = inc.get("severity", "medium").upper()
            color_hex = "#dc2626" if sev_badge == "CRITICAL" else "#ea580c" if sev_badge == "HIGH" else "#eab308"

            inc_title = f"<b>Incident #{idx:02d}: {inc.get('title')}</b> (<font color='{color_hex}'><b>{sev_badge}</b></font>)"
            inc_elements.append(Paragraph(inc_title, h2_style))
            inc_elements.append(Paragraph(f"<b>Time Window:</b> {inc.get('time_window')}", body_style))
            inc_elements.append(Paragraph(f"<b>ML Detection Triggers:</b> {inc.get('detector_triggers')}", body_style))
            inc_elements.append(Paragraph(f"<b>Probable Root Cause:</b> {inc.get('probable_root_cause')}", body_style))
            inc_elements.append(Paragraph(f"<b>AI Diagnostic Summary:</b> {inc.get('explanation')}", body_style))

            recs = inc.get("recommended_actions", [])
            if recs:
                inc_elements.append(Paragraph("<b>Recommended Actions:</b>", bold_label))
                for r in recs:
                    inc_elements.append(Paragraph(f"• {r}", body_style))

            inc_elements.append(Spacer(1, 8))
            elements.append(KeepTogether(inc_elements))

    doc.build(elements)
    buffer.seek(0)
    return buffer
