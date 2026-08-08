import asyncio
import datetime
import io
import json
import smtplib
from email.message import EmailMessage

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .config import settings
from .db import get_pool
from .integraciones import obtener
from .sqlguard import guard
from .supabase_db import run_sql


def _cot_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)


async def generar_pdf_dashboard(nombre: str, definicion: list[dict]) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=nombre, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story: list = [
        Paragraph(nombre, styles["Title"]),
        Paragraph(f"Generado: {_cot_now().strftime('%Y-%m-%d %H:%M')} (hora Colombia)", styles["Normal"]),
        Spacer(1, 14),
    ]
    for w in definicion:
        story.append(Paragraph(w.get("titulo", "Widget"), styles["Heading3"]))
        try:
            cols, filas = await run_sql(guard(w["sql"]))
            if cols:
                data = [cols] + [[str(f.get(c, "")) for c in cols] for f in filas[:50]]
                tbl = Table(data, repeatRows=1)
                tbl.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3b4fae")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("FONTSIZE", (0, 0), (-1, -1), 8),
                            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d0d5dd")),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f6f8")]),
                            ("PADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                story.append(tbl)
            else:
                story.append(Paragraph("Sin resultados.", styles["BodyText"]))
        except Exception as e:  # noqa: BLE001
            story.append(Paragraph(f"(No se pudo cargar: {e})", styles["BodyText"]))
        story.append(Spacer(1, 14))
    doc.build(story)
    buf.seek(0)
    return buf.read()


def _enviar_smtp(cfg: dict, destinatarios: str, asunto: str, cuerpo: str, pdf: bytes, filename: str):
    msg = EmailMessage()
    msg["From"] = cfg.get("from_email") or cfg["user"]
    msg["To"] = destinatarios
    msg["Subject"] = asunto
    msg.set_content(cuerpo)
    msg.add_attachment(pdf, maintype="application", subtype="pdf", filename=filename)
    port = int(cfg.get("port", 587))
    with smtplib.SMTP(cfg["host"], port, timeout=25) as s:
        if cfg.get("use_tls", True):
            s.starttls()
        s.login(cfg["user"], cfg["password"])
        s.send_message(msg)


async def enviar_informe(informe: dict) -> None:
    smtp = await obtener("smtp")
    if not smtp or not smtp.get("host") or not smtp.get("password"):
        raise RuntimeError("SMTP no está configurado. Ve a Configuración.")
    pool = await get_pool()
    async with pool.acquire() as con:
        d = await con.fetchrow(
            "select nombre, definicion from dashboards where id = $1", informe["dashboard_id"]
        )
    if d is None:
        raise RuntimeError("El dashboard del informe ya no existe.")
    definicion = json.loads(d["definicion"]) if isinstance(d["definicion"], str) else d["definicion"]
    pdf = await generar_pdf_dashboard(d["nombre"], definicion)
    await asyncio.to_thread(
        _enviar_smtp,
        smtp,
        informe["destinatarios"],
        f"Informe: {informe['nombre']}",
        f"Adjunto el informe automático '{informe['nombre']}' del tablero '{d['nombre']}'.",
        pdf,
        f"{informe['nombre']}.pdf",
    )


async def _tick():
    now = _cot_now()
    hhmm = now.strftime("%H:%M")
    hoy = now.date()
    es_habil = now.weekday() < 5
    pool = await get_pool()
    async with pool.acquire() as con:
        rows = await con.fetch("select * from informes_programados where activo = true")
    for r in rows:
        if r["ultimo_envio"] == hoy:
            continue
        if r["frecuencia"] == "habiles" and not es_habil:
            continue
        if hhmm < r["hora"]:
            continue
        try:
            await enviar_informe(dict(r))
            async with pool.acquire() as con:
                await con.execute(
                    "update informes_programados set ultimo_envio = $1 where id = $2", hoy, r["id"]
                )
        except Exception:  # noqa: BLE001 - un informe con error no debe frenar el resto
            pass


_ultima_limpieza = {"fecha": None}


async def _limpiar_historial():
    """Elimina conversaciones (y sus mensajes por cascada) más viejas que la retención. 1 vez/día."""
    hoy = _cot_now().date()
    if _ultima_limpieza["fecha"] == hoy:
        return
    pool = await get_pool()
    async with pool.acquire() as con:
        await con.execute(
            "delete from conversaciones where created_at < now() - make_interval(days => $1)",
            settings.chat_retencion_dias,
        )
    _ultima_limpieza["fecha"] = hoy


async def scheduler_loop():
    while True:
        try:
            await _tick()
            await _limpiar_historial()
        except Exception:  # noqa: BLE001
            pass
        await asyncio.sleep(60)
