from fastapi import APIRouter
from app.services.supabase import fetch

router = APIRouter()


@router.get("/")
async def get_agentes():
    """Lista de agentes activos con su extensión SIP y equipo"""
    try:
        data = await fetch("agentes", "activo=eq.true&order=nombres.asc")
        return {"data": data, "total": len(data)}
    except Exception as e:
        return {"error": str(e)}


@router.get("/estado")
async def get_estado_agentes():
    """Estado actual de todos los agentes en tiempo real"""
    try:
        data = await fetch("v_estado_agentes_actual")
        return {"data": data, "total": len(data)}
    except Exception as e:
        return {"error": str(e)}
