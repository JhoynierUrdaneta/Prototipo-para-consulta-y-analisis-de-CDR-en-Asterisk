from .db import get_pool

# Migraciones idempotentes de la BD del app que no vienen en el init inicial
# (para volúmenes ya creados en fases anteriores).
_SQL = """
-- Ampliar proveedores de integración permitidos (smtp y cloudflare)
alter table integraciones drop constraint if exists integraciones_proveedor_check;
alter table integraciones add constraint integraciones_proveedor_check
  check (proveedor in ('openai','supabase','smtp','cloudflare'));

create table if not exists informes_programados (
  id            uuid primary key default gen_random_uuid(),
  usuario_id    uuid not null references usuarios(id) on delete cascade,
  nombre        text not null,
  dashboard_id  uuid references dashboards(id) on delete cascade,
  destinatarios text not null,
  hora          text not null,
  frecuencia    text not null default 'diario',
  activo        boolean not null default true,
  ultimo_envio  date,
  created_at    timestamptz not null default now()
);
"""


async def migrar():
    pool = await get_pool()
    async with pool.acquire() as con:
        await con.execute(_SQL)
