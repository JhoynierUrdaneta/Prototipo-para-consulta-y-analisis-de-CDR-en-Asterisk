from fastapi import APIRouter, Depends, HTTPException, Request, status

from ..db import get_pool
from ..ratelimit import limit
from ..schemas import LoginIn, LoginOut, UserOut
from ..security import create_access_token, current_user, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _ip(request: Request) -> str:
    # Detrás de nginx, request.client es el contenedor; la IP real va en X-Real-IP
    # (ver frontend/nginx.conf).
    return request.headers.get("x-real-ip") or (
        request.client.host if request.client else "desconocida"
    )


@router.post("/login", response_model=LoginOut)
async def login(body: LoginIn, request: Request):
    # Freno a la fuerza bruta: por IP (estricto) y por cuenta (holgado, para no
    # permitir que un tercero bloquee a un usuario legítimo a propósito).
    aviso = "Demasiados intentos de inicio de sesión. Espera un minuto e inténtalo de nuevo."
    limit(f"login:ip:{_ip(request)}", 5, 60, aviso)
    limit(f"login:cuenta:{body.correo.lower()}", 10, 300, aviso)

    pool = await get_pool()
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "select id, correo, nombre, hash_password, perfil, activo "
            "from usuarios where correo = $1",
            body.correo.lower(),
        )
    if row is None or not row["activo"] or not verify_password(body.password, row["hash_password"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")

    token = create_access_token(str(row["id"]), row["perfil"], row["nombre"])
    return {
        "token": token,
        "usuario": {
            "id": str(row["id"]),
            "correo": row["correo"],
            "nombre": row["nombre"],
            "perfil": row["perfil"],
            "activo": row["activo"],
        },
    }


@router.get("/me", response_model=UserOut)
async def me(user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "select id, correo, nombre, perfil, activo from usuarios where id = $1", user["id"]
        )
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return {
        "id": str(row["id"]),
        "correo": row["correo"],
        "nombre": row["nombre"],
        "perfil": row["perfil"],
        "activo": row["activo"],
    }
