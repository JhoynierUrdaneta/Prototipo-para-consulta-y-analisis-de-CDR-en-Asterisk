from .crypto import decrypt_json, encrypt_json
from .db import get_pool


async def guardar(proveedor: str, data: dict, user_id: str) -> None:
    blob = encrypt_json(data)
    pool = await get_pool()
    async with pool.acquire() as con:
        await con.execute(
            "insert into integraciones (proveedor, datos_cifrados, actualizado_por, updated_at) "
            "values ($1, $2, $3, now()) "
            "on conflict (proveedor) do update set "
            "datos_cifrados = excluded.datos_cifrados, "
            "actualizado_por = excluded.actualizado_por, updated_at = now()",
            proveedor,
            blob,
            user_id,
        )


async def eliminar(proveedor: str) -> None:
    pool = await get_pool()
    async with pool.acquire() as con:
        await con.execute("delete from integraciones where proveedor = $1", proveedor)


async def obtener(proveedor: str) -> dict | None:
    """Config descifrada (uso interno). Incluye _updated_at. None si no existe."""
    pool = await get_pool()
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "select datos_cifrados, updated_at from integraciones where proveedor = $1", proveedor
        )
    if row is None:
        return None
    data = decrypt_json(row["datos_cifrados"])
    data["_updated_at"] = row["updated_at"].isoformat()
    return data
