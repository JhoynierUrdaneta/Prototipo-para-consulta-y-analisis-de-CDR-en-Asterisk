import json

from .config import settings
from .dashboard_iniciales import DASHBOARDS_INICIALES
from .db import get_pool
from .security import hash_password


async def seed_usuarios():
    """Crea los 4 usuarios iniciales (uno por perfil) si la tabla está vacía."""
    usuarios = [
        (settings.admin_email, "Administrador", settings.admin_password, "admin"),
        ("supervisor@estadiscall.com", "Supervisor", settings.supervisor_password, "supervisor"),
        ("coordinador@estadiscall.com", "Coordinador", settings.coordinador_password, "coordinador"),
        ("financiero@estadiscall.com", "Financiero", settings.financiero_password, "financiero"),
    ]
    pool = await get_pool()
    async with pool.acquire() as con:
        if await con.fetchval("select count(*) from usuarios") > 0:
            return
        for correo, nombre, pw, perfil in usuarios:
            await con.execute(
                "insert into usuarios (correo, nombre, hash_password, perfil) values ($1,$2,$3,$4)",
                correo.lower(),
                nombre,
                hash_password(pw),
                perfil,
            )


async def seed_dashboards():
    """Siembra los dashboards iniciales como compartidos (una sola vez, si no hay compartidos)."""
    pool = await get_pool()
    async with pool.acquire() as con:
        if await con.fetchval("select count(*) from dashboards where compartido = true") > 0:
            return
        admin_id = await con.fetchval(
            "select id from usuarios where perfil = 'admin' order by created_at limit 1"
        )
        if admin_id is None:
            return
        for d in DASHBOARDS_INICIALES:
            await con.execute(
                "insert into dashboards (usuario_id, nombre, definicion, compartido) "
                "values ($1, $2, $3::jsonb, true)",
                admin_id, d["nombre"], json.dumps(d["definicion"]),
            )
