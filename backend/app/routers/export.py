import base64
import io
import re

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..schemas import ExportExcelIn, ExportPdfIn
from ..security import current_user

router = APIRouter(prefix="/api/export", tags=["export"])

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.post("/excel")
async def excel(body: ExportExcelIn, _: dict = Depends(current_user)):
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"
    ws.append(body.columnas)
    for f in body.filas:
        ws.append([f.get(c) for c in body.columnas])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type=XLSX,
        headers={"Content-Disposition": 'attachment; filename="informe.xlsx"'},
    )


def _limpiar(texto: str) -> str:
    # Escapa XML y convierte **negrita** de markdown a <b> para reportlab.
    texto = texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)


@router.post("/pdf")
async def pdf(body: ExportPdfIn, _: dict = Depends(current_user)):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=body.titulo, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story: list = [Paragraph(_limpiar(body.titulo), styles["Title"]), Spacer(1, 12)]

    if body.chart_png and "," in body.chart_png:
        try:
            raw = base64.b64decode(body.chart_png.split(",", 1)[1])
            story.append(Image(io.BytesIO(raw), width=460, height=250))
            story.append(Spacer(1, 12))
        except Exception:  # noqa: BLE001 - si la imagen falla, seguimos sin ella
            pass

    if body.insight:
        story.append(Paragraph("<b>Análisis</b>", styles["Heading3"]))
        story.append(Paragraph(_limpiar(body.insight), styles["BodyText"]))
        story.append(Spacer(1, 8))

    if body.recomendaciones:
        story.append(Paragraph("<b>Recomendaciones</b>", styles["Heading3"]))
        for r in body.recomendaciones:
            story.append(Paragraph("• " + _limpiar(r), styles["BodyText"]))
        story.append(Spacer(1, 12))

    if body.columnas:
        data = [body.columnas] + [
            [str(f.get(c, "")) for c in body.columnas] for f in body.filas[:100]
        ]
        tbl = Table(data, repeatRows=1)
        tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b4fae")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d5dd")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f6f8")]),
                    ("PADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(tbl)

    doc.build(story)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="informe.pdf"'},
    )
