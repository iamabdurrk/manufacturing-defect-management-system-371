from __future__ import annotations

import io
from datetime import datetime

from bson import ObjectId
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.repositories.actions_repo import CorrectiveActionsRepository
from app.repositories.defects_repo import DefectsRepository, DefectTypesRepository
from app.repositories.rca_repo import RootCausesRepository
from app.utils.errors import NotFoundError
from app.utils.serialization import serialize_doc


class PdfExportService:
    """Generate audit-ready PDF report for a defect."""

    def __init__(self) -> None:
        self._defects = DefectsRepository()
        self._types = DefectTypesRepository()
        self._rca = RootCausesRepository()
        self._actions = CorrectiveActionsRepository()

    def export_defect_pdf(self, defect_id: str) -> bytes:
        defect = self._defects.find_by_id(ObjectId(defect_id))
        if not defect:
            raise NotFoundError("Defect not found")

        defect_type = self._types.find_by_id(defect.get("defect_type_id"))
        rc = self._rca.get_root_cause(ObjectId(defect_id))
        whys = self._rca.list_five_whys(ObjectId(defect_id))
        actions = self._actions.list_by_defect(ObjectId(defect_id))

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=LETTER)
        width, height = LETTER

        x = 0.75 * inch
        y = height - 0.75 * inch

        def line(text: str, dy: float = 14):
            nonlocal y
            c.drawString(x, y, text)
            y -= dy
            if y < 1.0 * inch:
                c.showPage()
                y = height - 0.75 * inch

        d = serialize_doc(defect)
        line("Manufacturing Defect Audit Report", dy=18)
        line(f"Generated: {datetime.utcnow().isoformat()}Z")
        line("")
        line(f"Defect ID: {d.get('_id')}")
        line(f"Part Number: {d.get('part_number')}")
        line(f"Defect Type: {serialize_doc(defect_type).get('name') if defect_type else str(d.get('defect_type_id'))}")
        line(f"Quantity Affected: {d.get('quantity_affected')}")
        line(f"Production Line: {d.get('production_line')}")
        line(f"Shift: {d.get('shift')}")
        line(f"Severity: {d.get('severity')}")
        line(f"Status: {d.get('status')}")
        line("")

        line("RCA", dy=16)
        if not rc:
            line("No root cause recorded.")
        else:
            rc_s = serialize_doc(rc)
            line(f"Method: {rc_s.get('method')}")
            if whys:
                line("5-Why Entries:")
                for w in serialize_doc(whys):
                    line(f"  {w.get('why_level')}. {w.get('description')}")
        line("")

        line("Corrective Actions", dy=16)
        if not actions:
            line("No corrective actions.")
        else:
            for a in serialize_doc(actions):
                line(f"- {a.get('description')}")
                line(f"  Status: {a.get('status')} | Due: {a.get('due_date')} | Completed: {a.get('completed_date')}")
                line("")

        line("Status Timeline", dy=16)
        for t in d.get("timeline", []) or []:
            line(f"- {t.get('status')} at {t.get('at')} by {t.get('by')}")

        c.showPage()
        c.save()
        return buf.getvalue()
