"""PDF export service for defects (audit-ready report)."""

from __future__ import annotations

import io
from typing import Any

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


class ExportService:
    """Generate PDF report bytes for a defect, including RCA and actions."""

    def build_defect_pdf(self, *, defect: dict[str, Any], rca: dict[str, Any] | None, actions: list[dict[str, Any]]) -> bytes:
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=LETTER)
        width, height = LETTER

        y = height - 0.75 * inch
        c.setFont("Helvetica-Bold", 16)
        c.drawString(0.75 * inch, y, f"Defect Report: {defect.get('id')}")
        y -= 0.4 * inch

        c.setFont("Helvetica", 11)
        fields = [
            ("Part Number", defect.get("part_number")),
            ("Defect Type", defect.get("defect_type_id")),
            ("Quantity Affected", defect.get("quantity_affected")),
            ("Production Line", defect.get("production_line")),
            ("Shift", defect.get("shift")),
            ("Severity", defect.get("severity")),
            ("Status", defect.get("status")),
            ("Created At", defect.get("created_at")),
            ("Updated At", defect.get("updated_at")),
        ]
        for label, value in fields:
            c.drawString(0.75 * inch, y, f"{label}: {value}")
            y -= 0.22 * inch
            if y < 1.5 * inch:
                c.showPage()
                y = height - 0.75 * inch
                c.setFont("Helvetica", 11)

        # RCA
        y -= 0.15 * inch
        c.setFont("Helvetica-Bold", 13)
        c.drawString(0.75 * inch, y, "Root Cause Analysis (RCA)")
        y -= 0.3 * inch
        c.setFont("Helvetica", 11)
        if not rca or not rca.get("method"):
            c.drawString(0.75 * inch, y, "No RCA recorded.")
            y -= 0.22 * inch
        else:
            c.drawString(0.75 * inch, y, f"Method: {rca.get('method')}")
            y -= 0.22 * inch
            if rca.get("method") == "5WHY":
                for i, why in enumerate(rca.get("five_whys") or [], start=1):
                    c.drawString(0.9 * inch, y, f"{i}. {why}")
                    y -= 0.2 * inch
            else:
                c.drawString(0.9 * inch, y, "Fishbone data included (see system).")
                y -= 0.2 * inch

        # Actions
        y -= 0.15 * inch
        c.setFont("Helvetica-Bold", 13)
        c.drawString(0.75 * inch, y, "Corrective Actions")
        y -= 0.3 * inch
        c.setFont("Helvetica", 11)
        if not actions:
            c.drawString(0.75 * inch, y, "No corrective actions recorded.")
            y -= 0.22 * inch
        else:
            for a in actions:
                line = f"- [{a.get('status')}] {a.get('description')} (Owner: {a.get('owner_id')}, Due: {a.get('due_date')})"
                # basic wrap
                while line:
                    chunk = line[:110]
                    line = line[110:]
                    c.drawString(0.75 * inch, y, chunk)
                    y -= 0.2 * inch
                    if y < 1.25 * inch:
                        c.showPage()
                        y = height - 0.75 * inch
                        c.setFont("Helvetica", 11)

        c.showPage()
        c.save()
        return buf.getvalue()
