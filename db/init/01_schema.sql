-- =====================================================================
-- BD del aplicativo (SEPARADA de Supabase). Usuarios, config cifrada,
-- conversaciones, dashboards y auditoría. Se ejecuta al iniciar el contenedor.
-- =====================================================================
create extension if not exists pgcrypto;

-- 4 perfiles del sistema
do $$ begin
  if not exists (select 1 from pg_type where typname = 'perfil_usuario') then
    create type perfil_usuario as enum ('admin','supervisor','coordinador','financiero');
  end if;
end $$;

create table if not exists usuarios (
  id            uuid primary key default gen_random_uuid(),
  correo        text unique not null,
  nombre        text not null,
  hash_password text not null,
  perfil        perfil_usuario not null,
  activo        boolean not null default true,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- Config de integraciones (OpenAI, Supabase). datos_cifrados = JSON cifrado (Fernet).
create table if not exists integraciones (
  proveedor       text primary key check (proveedor in ('openai','supabase','smtp','cloudflare')),
  datos_cifrados  bytea not null,
  actualizado_por uuid references usuarios(id),
  updated_at      timestamptz not null default now()
);

create table if not exists conversaciones (
  id         uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references usuarios(id) on delete cascade,
  titulo     text,
  created_at timestamptz not null default now()
);

create table if not exists mensajes (
  id              bigint generated always as identity primary key,
  conversacion_id uuid not null references conversaciones(id) on delete cascade,
  rol             text not null check (rol in ('user','assistant')),
  contenido       text,
  sql_generado    text,
  datos           jsonb,
  spec            jsonb,
  created_at      timestamptz not null default now()
);

create table if not exists dashboards (
  id         uuid primary key default gen_random_uuid(),
  usuario_id uuid not null references usuarios(id) on delete cascade,
  nombre     text not null,
  definicion jsonb not null,             -- lista de widgets {titulo, sql, tipo_grafico, ...}
  compartido boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Auditoría de cada consulta a Supabase
create table if not exists consultas_log (
  id           bigint generated always as identity primary key,
  usuario_id   uuid references usuarios(id) on delete set null,
  pregunta     text,
  sql_generado text,
  filas        integer,
  ms           integer,
  exito        boolean,
  error        text,
  created_at   timestamptz not null default now()
);

create index if not exists idx_conv_usuario on conversaciones(usuario_id);
create index if not exists idx_msg_conv     on mensajes(conversacion_id);
create index if not exists idx_dash_usuario on dashboards(usuario_id);
create index if not exists idx_log_created  on consultas_log(created_at);
