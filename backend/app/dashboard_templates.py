# Plantillas de dashboard por perfil. Cada widget trae SQL sobre las vistas de Supabase.
PLANTILLAS: dict[str, dict] = {
    "financiero": {
        "nombre": "Panel Financiero",
        "definicion": [
            {
                "titulo": "Costo por destino (hoy)",
                "sql": "select destino, round(sum(costo)) as costo from llamadas "
                "where fecha_hora_inicio >= current_date group by destino order by costo desc",
                "tipo_grafico": "bar", "eje_x": "destino", "series": ["costo"],
            },
            {
                "titulo": "Costo por campaña (hoy)",
                "sql": "select campania_codigo, round(costo_total) as costo from v_kpi_campania_dia "
                "where fecha = current_date order by costo desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["costo"],
            },
            {
                "titulo": "Ventas y monto por campaña (hoy)",
                "sql": "select campania_codigo, ventas, monto_ventas from v_kpi_campania_dia "
                "where fecha = current_date order by monto_ventas desc",
                "tipo_grafico": "table", "eje_x": "campania_codigo", "series": ["ventas", "monto_ventas"],
            },
        ],
    },
    "supervisor": {
        "nombre": "Panel de Operación",
        "definicion": [
            {
                "titulo": "Llamadas por estado (hoy)",
                "sql": "select estado_llamada, count(*) as total from llamadas "
                "where fecha_hora_inicio >= current_date group by estado_llamada order by total desc",
                "tipo_grafico": "pie", "eje_x": "estado_llamada", "series": ["total"],
            },
            {
                "titulo": "Contactabilidad por campaña (hoy)",
                "sql": "select campania_codigo, pct_contacto from v_kpi_campania_dia "
                "where fecha = current_date order by pct_contacto desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["pct_contacto"],
            },
            {
                "titulo": "Top agentes por contactadas (hoy)",
                "sql": "select agente, contestadas, ventas from v_kpi_agente_dia "
                "where fecha = current_date order by contestadas desc limit 10",
                "tipo_grafico": "table", "eje_x": "agente", "series": ["contestadas", "ventas"],
            },
        ],
    },
    "coordinador": {
        "nombre": "Panel Comparativo",
        "definicion": [
            {
                "titulo": "Llamadas por campaña (hoy)",
                "sql": "select campania_codigo, llamadas from v_kpi_campania_dia "
                "where fecha = current_date order by llamadas desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["llamadas"],
            },
            {
                "titulo": "Conversión por campaña (hoy)",
                "sql": "select campania_codigo, pct_conversion from v_kpi_campania_dia "
                "where fecha = current_date order by pct_conversion desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["pct_conversion"],
            },
            {
                "titulo": "Resumen del día",
                "sql": "select llamadas_hoy, contestadas, ventas, monto_ventas, costo_total from v_resumen_hoy",
                "tipo_grafico": "table", "eje_x": None, "series": [],
            },
        ],
    },
    "admin": {
        "nombre": "Panel General",
        "definicion": [
            {
                "titulo": "Resumen del día",
                "sql": "select llamadas_hoy, contestadas, ventas, monto_ventas, costo_total from v_resumen_hoy",
                "tipo_grafico": "table", "eje_x": None, "series": [],
            },
            {
                "titulo": "Llamadas por campaña (hoy)",
                "sql": "select campania_codigo, llamadas, contestadas from v_kpi_campania_dia "
                "where fecha = current_date order by llamadas desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["llamadas", "contestadas"],
            },
            {
                "titulo": "Costo por destino (hoy)",
                "sql": "select destino, round(sum(costo)) as costo from llamadas "
                "where fecha_hora_inicio >= current_date group by destino order by costo desc",
                "tipo_grafico": "pie", "eje_x": "destino", "series": ["costo"],
            },
        ],
    },
}
