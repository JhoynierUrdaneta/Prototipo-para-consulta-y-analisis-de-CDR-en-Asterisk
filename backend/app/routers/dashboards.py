import json

from fastapi import APIRouter, Depends, HTTPException, status

from ..dashboard_templates import PLANTILLAS
from ..db import get_pool
from ..schemas import DashboardIn, DashboardUpdate, WidgetSpec
from ..security import current_user

router = APIRouter(prefix="/api/dashboards", tags=["dashboards"])


def _row(r) -> dict:
    return {
        "id": str(r["id"]),
        "nombre": r["nombre"],
        "definicion": json.loads(r["definicion"]) if isinstance(r["definicion"], str) else r["definicion"],
        "compartido": r["compartido"],
        "es_propio": True,
    }


@router.get("")
async def listar(user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        rows = await con.fetch(
            "select id, nombre, definicion, compartido, usuario_id from dashboards "
            "where usuario_id = $1 or compartido = true order by created_at",
            user["id"],
        )
    out = []
    for r in rows:
        d = _row(r)
        d["es_propio"] = str(r["usuario_id"]) == user["id"]
        out.append(d)
    return out


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear(body: DashboardIn, user: dict = Depends(current_user)):
    definicion = [w.model_dump() for w in body.definicion]
    pool = await get_pool()
    async with pool.acquire() as con:
        r = await con.fetchrow(
            "insert into dashboards (usuario_id, nombre, definicion) values ($1,$2,$3::jsonb) "
            "returning id, nombre, definicion, compartido",
            user["id"], body.nombre, json.dumps(definicion),
        )
    return _row(r)


@router.post("/plantilla", status_code=status.HTTP_201_CREATED)
async def crear_desde_plantilla(user: dict = Depends(current_user)):
    tpl = PLANTILLAS.get(user["perfil"], PLANTILLAS["admin"])
    pool = await get_pool()
    async with pool.acquire() as con:
        r = await con.fetchrow(
            "insert into dashboards (usuario_id, nombre, definicion) values ($1,$2,$3::jsonb) "
            "returning id, nombre, definicion, compartido",
            user["id"], tpl["nombre"], json.dumps(tpl["definicion"]),
        )
    return _row(r)


@router.get("/{did}")
async def obtener(did: str, user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        r = await con.fetchrow(
            "select id, nombre, definicion, compartido, usuario_id from dashboards where id = $1", did
        )
    if r is None or (str(r["usuario_id"]) != user["id"] and not r["compartido"]):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dashboard no encontrado")
    return _row(r)


async def _propio_o_404(con, did, user):
    r = await con.fetchrow("select usuario_id from dashboards where id = $1", did)
    if r is None or str(r["usuario_id"]) != user["id"]:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dashboard no encontrado")


@router.patch("/{did}")
async def actualizar(did: str, body: DashboardUpdate, user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        await _propio_o_404(con, did, user)
        sets, args = [], []
        if body.nombre is not None:
            args.append(body.nombre); sets.append(f"nombre = ${len(args)}")
        if body.definicion is not None:
            args.append(json.dumps([w.model_dump() for w in body.definicion]))
            sets.append(f"definicion = ${len(args)}::jsonb")
        if body.compartido is not None:
            args.append(body.compartido); sets.append(f"compartido = ${len(args)}")
        if not sets:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nada que actualizar")
        sets.append("updated_at = now()")
        args.append(did)
        r = await con.fetchrow(
            f"update dashboards set {', '.join(sets)} where id = ${len(args)} "
            "returning id, nombre, definicion, compartido",
            *args,
        )
    return _row(r)


@router.post("/{did}/widgets", status_code=status.HTTP_201_CREATED)
async def agregar_widget(did: str, widget: WidgetSpec, user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        r = await con.fetchrow("select definicion, usuario_id from dashboards where id = $1", did)
        if r is None or str(r["usuario_id"]) != user["id"]:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Dashboard no encontrado")
        definicion = json.loads(r["definicion"]) if isinstance(r["definicion"], str) else r["definicion"]
        definicion.append(widget.model_dump())
        out = await con.fetchrow(
            "update dashboards set definicion = $1::jsonb, updated_at = now() where id = $2 "
            "returning id, nombre, definicion, compartido",
            json.dumps(definicion), did,
        )
    return _row(out)


@router.delete("/{did}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(did: str, user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        await _propio_o_404(con, did, user)
        await con.execute("delete from dashboards where id = $1", did)
