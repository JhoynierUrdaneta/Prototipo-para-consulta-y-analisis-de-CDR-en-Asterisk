import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..db import get_pool
from ..security import current_user

router = APIRouter(prefix="/api/conversaciones", tags=["conversaciones"])


class EliminarVarias(BaseModel):
    """Ids a borrar en una sola petición (evita N llamadas desde la UI)."""

    ids: list[str] = Field(min_length=1, max_length=200)


@router.get("")
async def listar(user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        rows = await con.fetch(
            "select id, titulo, created_at from conversaciones "
            "where usuario_id = $1 order by created_at desc",
            user["id"],
        )
    return [{"id": str(r["id"]), "titulo": r["titulo"], "created_at": r["created_at"].isoformat()} for r in rows]


@router.get("/{cid}/mensajes")
async def mensajes(cid: str, user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        propio = await con.fetchval(
            "select 1 from conversaciones where id = $1 and usuario_id = $2", cid, user["id"]
        )
        if not propio:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversación no encontrada")
        rows = await con.fetch(
            "select rol, contenido, datos from mensajes where conversacion_id = $1 order by id", cid
        )
    out = []
    for r in rows:
        datos = r["datos"]
        if isinstance(datos, str):
            datos = json.loads(datos)
        out.append({"rol": r["rol"], "contenido": r["contenido"], "datos": datos})
    return out


@router.post("/eliminar")
async def eliminar_varias(body: EliminarVarias, user: dict = Depends(current_user)):
    """Borra varias conversaciones del usuario en una sola operación.

    El filtro por usuario_id va en el propio DELETE: los ids que no le pertenezcan
    simplemente no se borran, sin revelar si existen.
    """
    try:
        ids = [uuid.UUID(i) for i in body.ids]
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Identificador de conversación inválido")

    pool = await get_pool()
    async with pool.acquire() as con:
        res = await con.execute(
            "delete from conversaciones where id = any($1::uuid[]) and usuario_id = $2",
            ids, user["id"],
        )
    # asyncpg devuelve "DELETE <n>"
    return {"eliminadas": int(res.rsplit(" ", 1)[-1])}


@router.delete("/{cid}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(cid: str, user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        res = await con.execute(
            "delete from conversaciones where id = $1 and usuario_id = $2", cid, user["id"]
        )
    if res.endswith("0"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversación no encontrada")
