import datetime
import uuid
from decimal import Decimal

import asyncpg

from .integraciones import obtener

_state: dict = {"pool": None, "dsn": None}


def _build_dsn(cfg: dict) -> str:
    return (
        f"postgresql://{cfg['db_user']}:{cfg['db_password']}"
        f"@{cfg['db_host']}:{cfg.get('db_port', 5432)}/{cfg.get('db_name', 'postgres')}"
    )


async def get_pool() -> asyncpg.Pool:
    cfg = await obtener("supabase")
    if not cfg or not cfg.get("db_host") or not cfg.get("db_password"):
        raise RuntimeError("Supabase no está configurado. Ve a Configuración.")
    dsn = _build_dsn(cfg)
    if _state["pool"] is None or _state["dsn"] != dsn:
        if _state["pool"] is not None:
            await _state["pool"].close()
        _state["pool"] = await asyncpg.create_pool(
            dsn,
            min_size=1,
            max_size=5,
            ssl="require",
            command_timeout=20,
        )
        _state["dsn"] = dsn
    return _state["pool"]


async def _preparar_sesion(con: asyncpg.Connection) -> None:
    """Fija statement_timeout y timezone por conexión con SET (no como parámetro de
    arranque): el pool de Supabase (Supavisor, modo transacción) rechaza parámetros
    de arranque no estándar como statement_timeout. El timezone es crítico -sin él,
    `current_date` se evalúa en UTC y a partir de las 19:00 hora Colombia todos los
    reportes de "hoy" salen vacíos."""
    await con.execute("SET statement_timeout = '15000'")
    await con.execute("SET timezone = 'America/Bogota'")


def _clean(v):
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime.datetime, datetime.date)):
        return v.isoformat()
    if isinstance(v, uuid.UUID):
        return str(v)
    return v


async def run_sql(sql_guarded: str) -> tuple[list[str], list[dict]]:
    pool = await get_pool()
    async with pool.acquire() as con:
        await _preparar_sesion(con)
        rows = await con.fetch(sql_guarded)
    cols = list(rows[0].keys()) if rows else []
    data = [{k: _clean(v) for k, v in r.items()} for r in rows]
    return cols, data


async def esquema_texto() -> str:
    """Introspección del esquema public (tablas, vistas y columnas) para el prompt del LLM."""
    pool = await get_pool()
    async with pool.acquire() as con:
        await _preparar_sesion(con)
        cols = await con.fetch(
            """
            select c.table_name, c.column_name, c.data_type,
                   t.table_type
            from information_schema.columns c
            join information_schema.tables t
              on t.table_schema = c.table_schema and t.table_name = c.table_name
            where c.table_schema = 'public'
            order by t.table_type desc, c.table_name, c.ordinal_position
            """
        )
    agrup: dict[str, dict] = {}
    for r in cols:
        item = agrup.setdefault(
            r["table_name"], {"tipo": "VISTA" if r["table_type"] == "VIEW" else "TABLA", "cols": []}
        )
        item["cols"].append(f'{r["column_name"]} {r["data_type"]}')
    lineas = []
    for nombre, info in agrup.items():
        lineas.append(f'{info["tipo"]} {nombre}(' + ", ".join(info["cols"]) + ")")
    return "\n".join(lineas)
