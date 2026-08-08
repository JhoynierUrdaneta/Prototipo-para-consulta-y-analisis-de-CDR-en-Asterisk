import json

from fastapi import APIRouter, Depends, HTTPException, status

from ..db import get_pool
from ..security import current_user

router = APIRouter(prefix="/api/conversaciones", tags=["conversaciones"])


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


@router.delete("/{cid}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(cid: str, user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        res = await con.execute(
            "delete from conversaciones where id = $1 and usuario_id = $2", cid, user["id"]
        )
    if res.endswith("0"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversación no encontrada")
