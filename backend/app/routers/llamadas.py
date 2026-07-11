from fastapi import APIRouter, Query
from app.services.supabase import fetch

router = APIRouter()


@router.get("/")
async def get_llamadas(
    limit: int = Query(default=100, le=500, description="Máximo número de registros"),
    estado: str = Query(default=None, description="Filtrar por estado: contestada, no_contesta, ocupado, abandonada, fallida"),
    campania_id: int = Query(default=None, description="Filtrar por ID de campaña"),
    agente_id: int = Query(default=None, description="Filtrar por ID de agente"),
):
    """Últimas llamadas con filtros opcionales"""
    try:
        params = f"order=fecha_hora_inicio.desc&limit={limit}"
        if estado:
            params += f"&estado_llamada=eq.{estado}"
        if campania_id:
            params += f"&campania_id=eq.{campania_id}"
        if agente_id:
            params += f"&agente_id=eq.{agente_id}"
        data = await fetch("v_llamadas_detalle", params)
        return {"data": data, "total": len(data)}
    except Exception as e:
        return {"error": str(e)}


@router.get("/estados")
async def get_estados_llamada():
    """Lista los valores posibles del campo estado_llamada"""
    return {
        "estados": [
            "contestada",
            "no_contesta",
            "ocupado",
            "abandonada",
            "buzon",
            "fallida"
        ]
    }
