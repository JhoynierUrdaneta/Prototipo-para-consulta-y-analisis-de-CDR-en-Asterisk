import datetime as dt

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import settings

ALGO = "HS256"
_bearer = HTTPBearer(auto_error=False)


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except ValueError:
        return False


def create_access_token(user_id: str, perfil: str, nombre: str) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": user_id,
        "perfil": perfil,
        "nombre": nombre,
        "iat": now,
        "exp": now + dt.timedelta(minutes=settings.jwt_expire_min),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGO)


async def current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if cred is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado")
    try:
        payload = jwt.decode(cred.credentials, settings.jwt_secret, algorithms=[ALGO])
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido o expirado")
    return {"id": payload["sub"], "perfil": payload["perfil"], "nombre": payload.get("nombre")}


def require_roles(*roles: str):
    async def dep(user: dict = Depends(current_user)) -> dict:
        if user["perfil"] not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Permiso insuficiente para esta acción")
        return user

    return dep
