"""Consultas operativas de solo lectura para Dashboard, Agentes y Campañas.

A diferencia de nlsql.py, aquí el SQL no lo genera la IA: son consultas fijas,
escritas y revisadas por el desarrollador, sobre las vistas y tablas de
Supabase. Se pasan igual por sqlguard.guard() como capa extra de seguridad.
"""

from .sqlguard import guard
from .supabase_db import run_sql


async def _query(sql: str) -> list[dict]:
    _, filas = await run_sql(guard(sql))
    return filas


async def resumen_hoy() -> dict:
    filas = await _query("select * from v_resumen_hoy")
    return filas[0] if filas else {}


async def kpi_campanias_hoy() -> list[dict]:
    return await _query(
        "select campania_codigo, campania, llamadas, contestadas, pct_contacto, "
        "ventas, costo_total, estado "
        "from v_kpi_campania_dia where fecha = current_date order by llamadas desc"
    )


async def estado_agentes_resumen() -> list[dict]:
    """Agrupa por el estado real (no por 'categoria': DISPONIBLE y EN_LLAMADA
    comparten categoría 'productivo' pero son cosas distintas para un supervisor).

    Se repite la expresión CASE en el GROUP BY (en vez de usar el alias "estado")
    porque v_estado_agentes_actual ya tiene una columna real llamada "estado":
    Postgres resuelve un GROUP BY ambiguo a favor de la columna de entrada, no
    del alias de salida, y eso rompía el agrupamiento.
    """
    caso = """
        case v.estado_codigo
          when 'DISPONIBLE' then 'Disponible'
          when 'EN_LLAMADA' then 'En llamada'
          when 'ACW' then 'En llamada'
          when 'PAUSA_BANIO' then 'En pausa'
          when 'PAUSA_ALMUERZO' then 'En pausa'
          when 'PAUSA_DESCANSO' then 'En pausa'
          when 'CAPACITACION' then 'Capacitación/reunión'
          when 'REUNION' then 'Capacitación/reunión'
          when 'DESCONECTADO' then 'Desconectado'
          else v.estado
        end
    """
    return await _query(
        f"""
        select {caso} as estado, count(*) as total
        from v_estado_agentes_actual v
        group by {caso}
        order by total desc
        """
    )


async def disposicion_hoy() -> list[dict]:
    return await _query(
        "select estado_llamada, count(*) as total from llamadas "
        "where fecha_hora_inicio >= current_date "
        "group by estado_llamada order by total desc"
    )


async def resumen_operativo() -> dict:
    """Todo lo que necesita el Dashboard, en un solo viaje al frontend."""
    return {
        "resumen": await resumen_hoy(),
        "campanias": await kpi_campanias_hoy(),
        "estado_agentes": await estado_agentes_resumen(),
        "disposicion": await disposicion_hoy(),
    }


async def lista_agentes() -> list[dict]:
    """Agentes activos con su estado en vivo, campaña de hoy y KPI del día."""
    return await _query(
        """
        select
          a.id, a.codigo_agente, a.nombres, a.apellidos,
          eq.nombre as equipo,
          c.codigo as campania_codigo,
          coalesce(v.estado_codigo, 'DESCONECTADO') as estado_codigo,
          coalesce(v.estado, 'Desconectado') as estado,
          coalesce(k.llamadas, 0) as llamadas,
          coalesce(k.ventas, 0) as ventas,
          k.tmo_seg
        from agentes a
        left join equipos eq on eq.id = a.equipo_id
        left join lateral (
          select cad.campania_id from campania_agentes_dia cad
          where cad.agente_id = a.id and cad.fecha = current_date
          limit 1
        ) cad on true
        left join campanias c on c.id = cad.campania_id
        left join v_estado_agentes_actual v on v.codigo_agente = a.codigo_agente
        left join v_kpi_agente_dia k
          on k.codigo_agente = a.codigo_agente and k.fecha = current_date
        where a.activo = true
        order by a.nombres, a.apellidos
        """
    )


async def top_agentes_ventas(limite: int = 10) -> list[dict]:
    return await _query(
        f"select agente, codigo_agente, equipo, llamadas, ventas, tmo_seg "
        f"from v_kpi_agente_dia where fecha = current_date "
        f"order by ventas desc, contestadas desc limit {int(limite)}"
    )


async def lista_campanias() -> list[dict]:
    """Campañas activas con su progreso del día (meta vs. llamadas reales)."""
    return await _query(
        """
        select
          c.id, c.codigo, c.nombre, c.modalidad, c.meta_llamadas_dia,
          tc.nombre as tipo_campania,
          coalesce(k.llamadas, 0) as llamadas,
          coalesce(k.contestadas, 0) as contestadas,
          coalesce(k.pct_contacto, 0) as pct_contacto,
          coalesce(k.ventas, 0) as ventas,
          coalesce(k.pct_conversion, 0) as pct_conversion,
          coalesce(k.monto_ventas, 0) as monto_ventas,
          coalesce(k.costo_total, 0) as costo_total,
          coalesce(k.tmo_seg, 0) as tmo_seg,
          coalesce(k.estado, 'activa') as estado
        from campanias c
        join tipos_campania tc on tc.id = c.tipo_campania_id
        left join v_kpi_campania_dia k
          on k.campania_codigo = c.codigo and k.fecha = current_date
        where c.activo = true
        order by c.codigo
        """
    )
