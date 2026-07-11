from fastapi import APIRouter
from app.services.supabase import fetch

router = APIRouter()


@router.get("/")
async def get_campanias():
    """Lista de campañas activas"""
    try:
        data = await fetch("campanias", "activo=eq.true&order=nombre.asc")
        return {"data": data, "total": len(data)}
    except Exception as e:
        return {"error": str(e)}
