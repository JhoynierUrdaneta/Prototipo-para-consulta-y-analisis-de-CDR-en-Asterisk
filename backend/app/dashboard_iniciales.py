# Dashboards iniciales de alto impacto. Se siembran como COMPARTIDOS (visibles para todos)
# la primera vez. Los usuarios pueden seguir creando dashboards propios y guardar widgets
# desde el chat con normalidad.

DASHBOARDS_INICIALES: list[dict] = [
    {
        "nombre": "① Resumen Ejecutivo",
        "definicion": [
            {
                "titulo": "Resumen del día",
                "sql": "select llamadas_hoy, contestadas, ventas, monto_ventas, costo_total from v_resumen_hoy",
                "tipo_grafico": "table", "eje_x": None, "series": [],
            },
            {
                "titulo": "Llamadas por estado (hoy)",
                "sql": "select estado_llamada, count(*) as cantidad from llamadas "
                "where fecha_hora_inicio >= current_date group by estado_llamada order by cantidad desc",
                "tipo_grafico": "pie", "eje_x": "estado_llamada", "series": ["cantidad"],
            },
            {
                "titulo": "Llamadas y contestadas por campaña (hoy)",
                "sql": "select campania_codigo, llamadas, contestadas from v_kpi_campania_dia "
                "where fecha = current_date order by llamadas desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["llamadas", "contestadas"],
            },
            {
                "titulo": "Costo por destino (hoy)",
                "sql": "select destino, round(sum(costo)) as costo from llamadas "
                "where fecha_hora_inicio >= current_date group by destino order by costo desc",
                "tipo_grafico": "bar", "eje_x": "destino", "series": ["costo"],
            },
        ],
    },
    {
        "nombre": "② Rendimiento de Campañas",
        "definicion": [
            {
                "titulo": "Contactabilidad por campaña (%) (hoy)",
                "sql": "select campania_codigo, pct_contacto from v_kpi_campania_dia "
                "where fecha = current_date order by pct_contacto desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["pct_contacto"],
            },
            {
                "titulo": "Conversión por campaña (%) (hoy)",
                "sql": "select campania_codigo, pct_conversion from v_kpi_campania_dia "
                "where fecha = current_date order by pct_conversion desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["pct_conversion"],
            },
            {
                "titulo": "TMO (seg) por campaña (hoy)",
                "sql": "select campania_codigo, tmo_seg from v_kpi_campania_dia "
                "where fecha = current_date order by tmo_seg desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["tmo_seg"],
            },
            {
                "titulo": "Ventas y monto por campaña (hoy)",
                "sql": "select campania_codigo, ventas, monto_ventas from v_kpi_campania_dia "
                "where fecha = current_date order by monto_ventas desc",
                "tipo_grafico": "table", "eje_x": "campania_codigo", "series": ["ventas", "monto_ventas"],
            },
        ],
    },
    {
        "nombre": "③ Rendimiento de Agentes",
        "definicion": [
            {
                "titulo": "Top 10 agentes por contestadas (hoy)",
                "sql": "select agente, contestadas, ventas from v_kpi_agente_dia "
                "where fecha = current_date order by contestadas desc limit 10",
                "tipo_grafico": "table", "eje_x": "agente", "series": ["contestadas", "ventas"],
            },
            {
                "titulo": "Top 10 agentes por ventas (hoy)",
                "sql": "select agente, ventas from v_kpi_agente_dia "
                "where fecha = current_date order by ventas desc limit 10",
                "tipo_grafico": "bar", "eje_x": "agente", "series": ["ventas"],
            },
            {
                "titulo": "Mejor contactabilidad por agente (%) (hoy, mín. 10 llamadas)",
                "sql": "select agente, round(100.0*contestadas/nullif(llamadas,0),2) as pct_contacto "
                "from v_kpi_agente_dia where fecha = current_date and llamadas >= 10 "
                "order by pct_contacto desc limit 10",
                "tipo_grafico": "bar", "eje_x": "agente", "series": ["pct_contacto"],
            },
        ],
    },
    {
        "nombre": "④ Panel Financiero",
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
                "titulo": "Monto de ventas por campaña (hoy)",
                "sql": "select campania_codigo, monto_ventas from v_kpi_campania_dia "
                "where fecha = current_date order by monto_ventas desc",
                "tipo_grafico": "bar", "eje_x": "campania_codigo", "series": ["monto_ventas"],
            },
            {
                "titulo": "Costo, ventas y monto del día",
                "sql": "select costo_total, ventas, monto_ventas from v_resumen_hoy",
                "tipo_grafico": "table", "eje_x": None, "series": [],
            },
        ],
    },
]
