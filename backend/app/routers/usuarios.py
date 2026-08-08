from fastapi import APIRouter, Depends, HTTPException, status

from ..db import get_pool
from ..schemas import UserCreate, UserOut, UserUpdate
from ..security import hash_password, require_roles

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


def _out(row) -> dict:
    return {
        "id": str(row["id"]),
        "correo": row["correo"],
        "nombre": row["nombre"],
        "perfil": row["perfil"],
        "activo": row["activo"],
    }


@router.get("", response_model=list[UserOut])
async def listar(_: dict = Depends(require_roles("admin"))):
    pool = await get_pool()
    async with pool.acquire() as con:
        rows = await con.fetch(
            "select id, correo, nombre, perfil, activo from usuarios order by created_at"
        )
    return [_out(r) for r in rows]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def crear(body: UserCreate, _: dict = Depends(require_roles("admin"))):
    pool = await get_pool()
    async with pool.acquire() as con:
        if await con.fetchval("select 1 from usuarios where correo = $1", body.correo.lower()):
            raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya está registrado")
        row = await con.fetchrow(
            "insert into usuarios (correo, nombre, hash_password, perfil) "
            "values ($1, $2, $3, $4) returning id, correo, nombre, perfil, activo",
            body.correo.lower(),
            body.nombre,
            hash_password(body.password),
            body.perfil,
        )
    return _out(row)


@router.patch("/{uid}", response_model=UserOut)
async def actualizar(uid: str, body: UserUpdate, _: dict = Depends(require_roles("admin"))):
    sets, args = [], []
    if body.nombre is not None:
        args.append(body.nombre); sets.append(f"nombre = ${len(args)}")
    if body.perfil is not None:
        args.append(body.perfil); sets.append(f"perfil = ${len(args)}")
    if body.activo is not None:
        args.append(body.activo); sets.append(f"activo = ${len(args)}")
    if body.password is not None:
        args.append(hash_password(body.password)); sets.append(f"hash_password = ${len(args)}")
    if not sets:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nada que actualizar")
    sets.append("updated_at = now()")
    args.append(uid)
    pool = await get_pool()
    async with pool.acquire() as con:
        row = await con.fetchrow(
            f"update usuarios set {', '.join(sets)} where id = ${len(args)} "
            "returning id, correo, nombre, perfil, activo",
            *args,
        )
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return _out(row)


@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar(uid: str, _: dict = Depends(require_roles("admin"))):
    # Baja lógica para preservar el histórico de conversaciones/consultas.
    pool = await get_pool()
    async with pool.acquire() as con:
        res = await con.execute("update usuarios set activo = false where id = $1", uid)
    if res.endswith("0"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
