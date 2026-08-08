import asyncio
import smtplib

import asyncpg
import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from ..integraciones import eliminar, guardar, obtener
from ..schemas import CloudflareConfig, OpenAIConfig, SMTPConfig, SupabaseConfig
from ..security import require_roles

router = APIRouter(prefix="/api/config", tags=["config"])


def _mask(s: str | None) -> str:
    if not s:
        return ""
    return "••••" + s[-4:] if len(s) > 4 else "••••"


# ============================ OpenAI ============================
@router.get("/openai")
async def get_openai(_: dict = Depends(require_roles("admin"))):
    cfg = await obtener("openai")
    if not cfg:
        return {"configurado": False, "model": "gpt-4o"}
    return {
        "configurado": True,
        "model": cfg.get("model", "gpt-4o"),
        "base_url": cfg.get("base_url"),
        "api_key_mask": _mask(cfg.get("api_key")),
        "updated_at": cfg.get("_updated_at"),
    }


@router.put("/openai")
async def put_openai(body: OpenAIConfig, user: dict = Depends(require_roles("admin"))):
    data = body.model_dump(exclude_none=True)
    if not data.get("api_key"):
        existing = await obtener("openai")
        if existing and existing.get("api_key"):
            data["api_key"] = existing["api_key"]
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Falta la API key de OpenAI")
    await guardar("openai", data, user["id"])
    return {"ok": True}


async def _probar_openai(api_key: str, base_url: str | None) -> dict:
    url = (base_url or "https://api.openai.com/v1").rstrip("/") + "/models"
    try:
        async with httpx.AsyncClient(timeout=15) as cli:
            r = await cli.get(url, headers={"Authorization": f"Bearer {api_key}"})
    except httpx.HTTPError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No se pudo conectar a OpenAI: {e}")
    if r.status_code == 200:
        return {"ok": True, "modelos_disponibles": len(r.json().get("data", []))}
    raise HTTPException(status.HTTP_400_BAD_REQUEST, f"OpenAI respondió HTTP {r.status_code}")


@router.post("/openai/test")
async def test_openai(body: OpenAIConfig, _: dict = Depends(require_roles("admin"))):
    api_key = body.api_key
    base_url = body.base_url
    if not api_key:  # usar la almacenada
        existing = await obtener("openai")
        if not existing or not existing.get("api_key"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No hay API key para probar")
        api_key = existing["api_key"]
        base_url = base_url or existing.get("base_url")
    return await _probar_openai(api_key, base_url)


# ============================ Supabase ============================
@router.get("/supabase")
async def get_supabase(_: dict = Depends(require_roles("admin"))):
    cfg = await obtener("supabase")
    if not cfg:
        return {"configurado": False, "db_port": 5432, "db_name": "postgres"}
    return {
        "configurado": True,
        "url": cfg.get("url"),
        "db_host": cfg.get("db_host"),
        "db_port": cfg.get("db_port", 5432),
        "db_name": cfg.get("db_name", "postgres"),
        "db_user": cfg.get("db_user"),
        "db_password_mask": _mask(cfg.get("db_password")),
        "anon_key_mask": _mask(cfg.get("anon_key")),
        "updated_at": cfg.get("_updated_at"),
    }


@router.put("/supabase")
async def put_supabase(body: SupabaseConfig, user: dict = Depends(require_roles("admin"))):
    data = body.model_dump(exclude_none=True)
    if not data.get("db_password"):
        existing = await obtener("supabase")
        if existing and existing.get("db_password"):
            data["db_password"] = existing["db_password"]
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Falta la contraseña de la base")
    await guardar("supabase", data, user["id"])
    return {"ok": True}


async def _probar_supabase(cfg: dict) -> dict:
    dsn = (
        f"postgresql://{cfg['db_user']}:{cfg['db_password']}"
        f"@{cfg['db_host']}:{cfg.get('db_port', 5432)}/{cfg.get('db_name', 'postgres')}"
    )
    try:
        con = await asyncpg.connect(dsn, timeout=10, ssl="require")
    except Exception as e:  # noqa: BLE001 - reportar el motivo al admin
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No se pudo conectar a Supabase: {e}")
    try:
        ver = await con.fetchval("show server_version")
        tablas = await con.fetchval(
            "select count(*) from information_schema.tables where table_schema = 'public'"
        )
    finally:
        await con.close()
    return {"ok": True, "server_version": ver, "tablas_public": tablas}


@router.post("/supabase/test")
async def test_supabase(body: SupabaseConfig, _: dict = Depends(require_roles("admin"))):
    cfg = body.model_dump(exclude_none=True)
    if not cfg.get("db_password"):
        existing = await obtener("supabase")
        if not existing or not existing.get("db_password"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No hay contraseña para probar")
        cfg["db_password"] = existing["db_password"]
    return await _probar_supabase(cfg)


# ============================ SMTP (correo) ============================
@router.get("/smtp")
async def get_smtp(_: dict = Depends(require_roles("admin"))):
    cfg = await obtener("smtp")
    if not cfg:
        return {"configurado": False, "port": 587, "use_tls": True}
    return {
        "configurado": True,
        "host": cfg.get("host"),
        "port": cfg.get("port", 587),
        "user": cfg.get("user"),
        "from_email": cfg.get("from_email"),
        "use_tls": cfg.get("use_tls", True),
        "password_mask": _mask(cfg.get("password")),
        "updated_at": cfg.get("_updated_at"),
    }


@router.put("/smtp")
async def put_smtp(body: SMTPConfig, user: dict = Depends(require_roles("admin"))):
    data = body.model_dump(exclude_none=True)
    if not data.get("password"):
        existing = await obtener("smtp")
        if existing and existing.get("password"):
            data["password"] = existing["password"]
        else:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Falta la contraseña SMTP")
    await guardar("smtp", data, user["id"])
    return {"ok": True}


def _probar_smtp_sync(cfg: dict) -> None:
    with smtplib.SMTP(cfg["host"], int(cfg.get("port", 587)), timeout=15) as s:
        if cfg.get("use_tls", True):
            s.starttls()
        s.login(cfg["user"], cfg["password"])


@router.post("/smtp/test")
async def test_smtp(body: SMTPConfig, _: dict = Depends(require_roles("admin"))):
    cfg = body.model_dump(exclude_none=True)
    if not cfg.get("password"):
        existing = await obtener("smtp")
        if not existing or not existing.get("password"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No hay contraseña para probar")
        cfg["password"] = existing["password"]
    try:
        await asyncio.to_thread(_probar_smtp_sync, cfg)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"No se pudo conectar al SMTP: {e}")
    return {"ok": True}


# ============================ Cloudflare Tunnel ============================
@router.get("/cloudflare")
async def get_cloudflare(_: dict = Depends(require_roles("admin"))):
    cfg = await obtener("cloudflare")
    if not cfg:
        return {"configurado": False}
    return {
        "configurado": True,
        "token_mask": _mask(cfg.get("tunnel_token")),
        "updated_at": cfg.get("_updated_at"),
    }


@router.put("/cloudflare")
async def put_cloudflare(body: CloudflareConfig, user: dict = Depends(require_roles("admin"))):
    # El contenedor cloudflared consulta este token (endpoint interno) y levanta el túnel solo.
    await guardar("cloudflare", {"tunnel_token": body.tunnel_token}, user["id"])
    return {"ok": True}


@router.delete("/cloudflare", status_code=status.HTTP_204_NO_CONTENT)
async def del_cloudflare(_: dict = Depends(require_roles("admin"))):
    await eliminar("cloudflare")
