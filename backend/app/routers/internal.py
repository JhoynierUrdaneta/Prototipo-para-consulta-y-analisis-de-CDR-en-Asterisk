from fastapi import APIRouter, Header, HTTPException, status

from ..config import settings
from ..integraciones import obtener

# Endpoints internos (no bajo /api, no proxiados por nginx). Solo accesibles dentro
# de la red de Docker y protegidos por una clave compartida.
router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/cloudflare-token")
async def cloudflare_token(x_internal_key: str = Header(default="")):
    if x_internal_key != settings.internal_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autorizado")
    cfg = await obtener("cloudflare")
    return {"token": cfg.get("tunnel_token") if cfg else None}
