import json
import time

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..config import settings
from ..db import get_pool
from ..nlsql import responder
from ..ratelimit import limit
from ..security import current_user, require_roles
from ..sqlguard import SQLError, guard
from ..supabase_db import esquema_texto, run_sql

router = APIRouter(prefix="/api/consulta", tags=["consulta"])


class ConsultaIn(BaseModel):
    pregunta: str = Field(min_length=3, max_length=500)
    conversacion_id: str | None = None
    aclaraciones: dict | None = None


class SQLIn(BaseModel):
    sql: str


class WidgetIn(BaseModel):
    """Identifica un widget por su tablero y posición; el SQL lo pone el servidor."""

    dashboard_id: str
    widget_index: int = Field(ge=0)


async def _log(user_id, pregunta, sql, filas, ms, exito, error):
    pool = await get_pool()
    async with pool.acquire() as con:
        await con.execute(
            "insert into consultas_log (usuario_id, pregunta, sql_generado, filas, ms, exito, error) "
            "values ($1,$2,$3,$4,$5,$6,$7)",
            user_id, pregunta, sql, filas, ms, exito, error,
        )


async def _persistir_chat(user_id, conv_id, pregunta, res) -> str:
    """Guarda el turno (pregunta + respuesta con datos) en conversaciones/mensajes."""
    pool = await get_pool()
    async with pool.acquire() as con:
        if conv_id:
            propio = await con.fetchval(
                "select 1 from conversaciones where id = $1 and usuario_id = $2", conv_id, user_id
            )
            if not propio:
                conv_id = None
        if not conv_id:
            conv_id = await con.fetchval(
                "insert into conversaciones (usuario_id, titulo) values ($1, $2) returning id",
                user_id, pregunta[:80],
            )
        conv_id = str(conv_id)
        await con.execute(
            "insert into mensajes (conversacion_id, rol, contenido) values ($1, 'user', $2)",
            conv_id, pregunta,
        )
        await con.execute(
            "insert into mensajes (conversacion_id, rol, contenido, sql_generado, datos) "
            "values ($1, 'assistant', $2, $3, $4::jsonb)",
            conv_id, res.get("insight"), res.get("sql"), json.dumps(res),
        )
    return conv_id


@router.post("")
async def consultar(body: ConsultaIn, user: dict = Depends(current_user)):
    limit(f"consulta:{user['id']}", settings.consulta_max_por_min, 60)
    try:
        res = await responder(body.pregunta, user["perfil"], body.aclaraciones)
    except SQLError as e:
        await _log(user["id"], body.pregunta, None, None, None, False, str(e))
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Consulta no permitida: {e}")
    except RuntimeError as e:
        await _log(user["id"], body.pregunta, None, None, None, False, str(e))
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    except Exception as e:  # noqa: BLE001
        await _log(user["id"], body.pregunta, None, None, None, False, str(e))
        # 400 (no 5xx) para que el frontend muestre un mensaje claro y el proxy/Cloudflare
        # no lo interprete como "origen caído".
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "No se pudo procesar la consulta. Intenta reformularla."
        )
    # Si solo pide aclaración, no se registra ni se persiste (aún no hay reporte).
    if res.get("tipo") == "aclaracion":
        return res
    await _log(user["id"], body.pregunta, res["sql"], res["n_filas"], res["ms"], True, None)
    res["conversacion_id"] = await _persistir_chat(user["id"], body.conversacion_id, body.pregunta, res)
    return res


@router.post("/sql")
async def consultar_sql(body: SQLIn, user: dict = Depends(require_roles("admin"))):
    """Ejecuta SQL crudo a través del guard (sin IA). Útil para pruebas y power-users admin."""
    try:
        sql_guarded = guard(body.sql)
    except SQLError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    t0 = time.monotonic()
    try:
        columnas, filas = await run_sql(sql_guarded)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Error de ejecución: {e}")
    return {"columnas": columnas, "filas": filas, "n_filas": len(filas), "ms": int((time.monotonic() - t0) * 1000)}


@router.post("/ejecutar")
async def ejecutar(body: WidgetIn, user: dict = Depends(current_user)):
    """Ejecuta el SQL guardado de un widget.

    El SQL se lee del servidor a partir del tablero y la posición del widget:
    nunca se acepta SQL del cliente. Antes este endpoint recibía la consulta en
    el cuerpo, lo que permitía a cualquier usuario autenticado ejecutar SELECTs
    arbitrarios contra Supabase, saltándose el control por perfil.
    """
    pool = await get_pool()
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "select definicion, usuario_id, compartido from dashboards where id = $1",
            body.dashboard_id,
        )
    # Mismo criterio de acceso que GET /api/dashboards/{id}: propio o compartido.
    if row is None or (str(row["usuario_id"]) != user["id"] and not row["compartido"]):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tablero no encontrado")

    definicion = row["definicion"]
    if isinstance(definicion, str):
        definicion = json.loads(definicion)
    if not 0 <= body.widget_index < len(definicion):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Widget no encontrado")

    try:
        sql_guarded = guard(definicion[body.widget_index]["sql"])
    except SQLError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    try:
        columnas, filas = await run_sql(sql_guarded)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Error de ejecución: {e}")
    return {"columnas": columnas, "filas": filas, "n_filas": len(filas)}


@router.get("/esquema")
async def ver_esquema(_: dict = Depends(require_roles("admin"))):
    return {"esquema": await esquema_texto()}
