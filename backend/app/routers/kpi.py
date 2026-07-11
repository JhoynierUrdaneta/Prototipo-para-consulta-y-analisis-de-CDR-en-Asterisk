from fastapi import APIRouter, Query
from app.services.supabase import fetch

router = APIRouter()


@router.get("/campanias")
async def get_kpi_campanias(
    fecha: str = Query(default=None, description="Fecha en formato YYYY-MM-DD. Si no se pasa, trae hoy.")
):
    """KPIs por campaña: llamadas, contestadas, ventas, costo, TMO"""
    try:
        params = "order=llamadas.desc"
        if fecha:
            params += f"&fecha=eq.{fecha}"
        data = await fetch("v_kpi_campania_dia", params)
        return {"data": data, "total": len(data)}
    except Exception as e:
        return {"error": str(e)}


@router.get("/agentes")
async def get_kpi_agentes(
    fecha: str = Query(default=None, description="Fecha en formato YYYY-MM-DD. Si no se pasa, trae hoy."),
    limit: int = Query(default=50, le=200)
):
    """KPIs por agente: llamadas, ventas, duración promedio, costo generado"""
    try:
        params = f"order=ventas.desc&limit={limit}"
        if fecha:
            params += f"&fecha=eq.{fecha}"
        data = await fetch("v_kpi_agente_dia", params)
        return {"data": data, "total": len(data)}
    except Exception as e:
        return {"error": str(e)}
