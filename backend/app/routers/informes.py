from fastapi import APIRouter, Depends, HTTPException, status

from ..db import get_pool
from ..informes import _cot_now, enviar_informe
from ..schemas import InformeIn, InformeUpdate
from ..security import current_user

router = APIRouter(prefix="/api/informes", tags=["informes"])


def _row(r) -> dict:
    return {
        "id": str(r["id"]),
        "nombre": r["nombre"],
        "dashboard_id": str(r["dashboard_id"]) if r["dashboard_id"] else None,
        "destinatarios": r["destinatarios"],
        "hora": r["hora"],
        "frecuencia": r["frecuencia"],
        "activo": r["activo"],
        "ultimo_envio": r["ultimo_envio"].isoformat() if r["ultimo_envio"] else None,
    }


@router.get("")
async def listar(user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        rows = await con.fetch(
            "select * from informes_programados where usuario_id = $1 order by created_at", user["id"]
        )
    return [_row(r) for r in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
async def crear(body: InformeIn, user: dict = Depends(current_user)):
    # Si la hora programada ya pasó hoy, se marca el día como enviado para que
    # el scheduler empiece mañana. Sin esto, programar algo a las 08:00 siendo
    # el mediodía dispara un envío inmediato, que el usuario no pidió.
    ahora = _cot_now()
    ya_paso = ahora.strftime("%H:%M") >= body.hora
    ultimo_envio = ahora.date() if ya_paso else None

    pool = await get_pool()
    async with pool.acquire() as con:
        r = await con.fetchrow(
            "insert into informes_programados "
            "(usuario_id, nombre, dashboard_id, destinatarios, hora, frecuencia, ultimo_envio) "
            "values ($1,$2,$3,$4,$5,$6,$7) returning *",
            user["id"], body.nombre, body.dashboard_id, body.destinatarios,
            body.hora, body.frecuencia, ultimo_envio,
        )
    return _row(r)


@router.patch("/{iid}")
async def actualizar(iid: str, body: InformeUpdate, user: dict = Depends(current_user)):
    sets, args = [], []
    for campo in ("nombre", "destinatarios", "hora", "frecuencia", "activo"):
        val = getattr(body, campo)
        if val is not None:
            args.append(val); sets.append(f"{campo} = ${len(args)}")
    if not sets:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nada que actualizar")
    args.extend([iid, user["id"]])
    pool = await get_pool()
    async with pool.acquire() as con:
        r = await con.fetchrow(
            f"update informes_programados set {', '.join(sets)} "
            f"where id = ${len(args)-1} and usuario_id = ${len(args)} returning *",
            *args,
        )
    if r is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Informe no encontrado")
    return _row(r)


@router.delete("/{iid}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(iid: str, user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        res = await con.execute(
            "delete from informes_programados where id = $1 and usuario_id = $2", iid, user["id"]
        )
    if res.endswith("0"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Informe no encontrado")


@router.post("/{iid}/enviar")
async def enviar_ahora(iid: str, user: dict = Depends(current_user)):
    pool = await get_pool()
    async with pool.acquire() as con:
        r = await con.fetchrow(
            "select * from informes_programados where id = $1 and usuario_id = $2", iid, user["id"]
        )
    if r is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Informe no encontrado")
    try:
        await enviar_informe(dict(r))
    except RuntimeError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"No se pudo enviar: {e}")
    return {"ok": True}
