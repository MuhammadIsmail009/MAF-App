from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def build_pdf_report(
    metadata: Dict[str, Any],
    volatility_output: Optional[Dict[str, Any]],
    ml_output: Optional[Dict[str, Any]],
    dl_output: Optional[Dict[str, Any]],
    alerts: List[Dict[str, Any]],
    analyst_name: Optional[str] = None,
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    story: List[Any] = []

    story.append(Paragraph("AI-Based Memory Forensics Report", styles["Title"]))
    story.append(Spacer(1, 12))

    # Evidence metadata
    story.append(Paragraph("<b>Evidence Metadata</b>", styles["Heading2"]))
    for key in ["filename", "sha256", "size_bytes", "case_id", "timestamp"]:
        if key in metadata:
            story.append(Paragraph(f"{key}: {metadata[key]}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # ALERT SUMMARY
    story.append(Paragraph("<b>ALERT SUMMARY</b>", styles["Heading2"]))
    if alerts:
        for a in alerts:
            line = (
                f"{a.get('created_at')}: {a.get('process_name')} (PID {a.get('pid')}) "
                f"label={a.get('label')} anomaly={a.get('anomaly_score'):.2f} "
                f"confidence={a.get('ml_confidence', 0.0):.2f}"
            )
            story.append(Paragraph(line, styles["Normal"]))
    else:
        story.append(Paragraph("No alerts generated.", styles["Normal"]))
    story.append(Spacer(1, 12))

    # High-level AI/DL summary
    story.append(Paragraph("<b>AI / ML Summary</b>", styles["Heading2"]))
    if ml_output:
        story.append(
            Paragraph(
                f"Max anomaly score: {ml_output.get('max_anomaly_score', 0.0):.2f}", styles["Normal"]
            )
        )
        story.append(
            Paragraph(
                f"Any malicious: {ml_output.get('any_malicious', False)}", styles["Normal"]
            )
        )
    if dl_output:
        story.append(
            Paragraph(
                f"DL string analysis score: {dl_output.get('dl_score', 0.0):.2f}", styles["Normal"]
            )
        )
    story.append(Spacer(1, 12))

    # Volatility results (summary only)
    story.append(Paragraph("<b>Volatility Artifacts</b>", styles["Heading2"]))
    if volatility_output:
        pslist = volatility_output.get("pslist") or []
        story.append(Paragraph(f"Total processes: {len(pslist)}", styles["Normal"]))
        netscan = volatility_output.get("netscan") or []
        story.append(Paragraph(f"Network connections: {len(netscan)}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Placeholder for images (process tree, network graph)
    story.append(Paragraph("<b>Visual Artifacts</b>", styles["Heading2"]))
    story.append(Paragraph("Process tree image: [to be attached by frontend].", styles["Normal"]))
    story.append(Paragraph("Network graph image: [to be attached by frontend].", styles["Normal"]))
    story.append(Spacer(1, 24))

    # Analyst signature
    story.append(Paragraph("<b>Analyst</b>", styles["Heading2"]))
    story.append(Paragraph(f"Name: {analyst_name or '________________'}", styles["Normal"]))
    story.append(Paragraph("Signature: _______________________________", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()



