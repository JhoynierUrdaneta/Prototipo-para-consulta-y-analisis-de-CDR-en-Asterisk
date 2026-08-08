import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import get_pool
from .informes import scheduler_loop
from .migrate import migrar
from .routers import (
    auth,
    config,
    consulta,
    conversaciones,
    dashboards,
    export,
    informes,
    internal,
    usuarios,
)
from .seed import seed_dashboards, seed_usuarios

log = logging.getLogger("callcenter-ai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
    await migrar()
    await seed_usuarios()
    await seed_dashboards()
    if settings.env == "production" and (
        settings.app_secret_key.startswith("dev-") or settings.jwt_secret.startswith("dev-")
    ):
        log.warning("SEGURIDAD: APP_SECRET_KEY/JWT_SECRET usan valores por defecto en producción.")
    tarea = asyncio.create_task(scheduler_loop())
    try:
        yield
    finally:
        tarea.cancel()


app = FastAPI(title="Call Center AI", version="0.3.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def cabeceras_seguridad(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(config.router)
app.include_router(consulta.router)
app.include_router(conversaciones.router)
app.include_router(dashboards.router)
app.include_router(export.router)
app.include_router(informes.router)
app.include_router(internal.router)


@app.get("/api/health")
async def health():
    pool = await get_pool()
    async with pool.acquire() as con:
        await con.fetchval("select 1")
    return {"status": "ok", "service": "callcenter-ai-backend", "version": "0.3.0"}
