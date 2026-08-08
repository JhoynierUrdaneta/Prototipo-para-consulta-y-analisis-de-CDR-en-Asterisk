from fastapi import APIRouter, Depends, HTTPException, status

from .. import panel
from ..security import current_user

router = APIRouter(prefix="/api/panel", tags=["panel"])


@router.get("/resumen")
async def resumen(_: dict = Depends(current_user)):
    try:
        return await panel.resumen_operativo()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No se pudo cargar el resumen: {e}")


@router.get("/agentes")
async def agentes(_: dict = Depends(current_user)):
    try:
        return {
            "agentes": await panel.lista_agentes(),
            "top_ventas": await panel.top_agentes_ventas(),
        }
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No se pudieron cargar los agentes: {e}")


@router.get("/campanias")
async def campanias(_: dict = Depends(current_user)):
    try:
        return {"campanias": await panel.lista_campanias()}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No se pudieron cargar las campañas: {e}")
