from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import llamadas, kpi, agentes, campanias, chat

app = FastAPI(
    title="Estadis-Call API",
    description="API para consulta y análisis de CDR con IA — BPO Barranquilla",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(llamadas.router,  prefix="/llamadas",  tags=["Llamadas"])
app.include_router(kpi.router,       prefix="/kpi",       tags=["KPI"])
app.include_router(agentes.router,   prefix="/agentes",   tags=["Agentes"])
app.include_router(campanias.router, prefix="/campanias", tags=["Campañas"])
app.include_router(chat.router,      prefix="/chat",      tags=["Chat IA"])


@app.get("/", tags=["Health"])
def root():
    return {"mensaje": "Estadis-Call API funcionando correctamente", "version": "2.0.0"}


@app.get("/resumen", tags=["Health"])
async def get_resumen():
    """Resumen general de la operación del día"""
    from app.services.supabase import fetch
    try:
        data = await fetch("v_resumen_hoy")
        return data
    except Exception as e:
        return {"error": str(e)}


@app.get("/stats", tags=["Health"])
async def get_stats():
    """Indicadores estadísticos generales del tráfico de llamadas"""
    from app.services.supabase import fetch
    try:
        data = await fetch("llamadas", "select=estado_llamada,duracion_seg,costo,es_venta")
        total = len(data)
        contestadas  = len([x for x in data if x.get("estado_llamada") == "contestada"])
        no_contesta  = len([x for x in data if x.get("estado_llamada") == "no_contesta"])
        ocupado      = len([x for x in data if x.get("estado_llamada") == "ocupado"])
        abandonadas  = len([x for x in data if x.get("estado_llamada") == "abandonada"])
        ventas       = len([x for x in data if x.get("es_venta") is True])
        duracion_prom = round(
            sum(x.get("duracion_seg", 0) for x in data) / total if total > 0 else 0, 2
        )
        costo_total = round(
            sum(float(x.get("costo", 0) or 0) for x in data), 2
        )
        return {
            "total_llamadas":       total,
            "contestadas":          contestadas,
            "no_contesta":          no_contesta,
            "ocupado":              ocupado,
            "abandonadas":          abandonadas,
            "ventas":               ventas,
            "duracion_promedio_seg": duracion_prom,
            "costo_total":          costo_total,
        }
    except Exception as e:
        return {"error": str(e)}
