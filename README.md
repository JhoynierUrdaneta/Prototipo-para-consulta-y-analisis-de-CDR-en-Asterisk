# Estadis-Call — Analítica de call center con IA

Plataforma para consultar los datos de un call center **preguntando en español**.
Una IA traduce la pregunta a SQL, la ejecuta sobre la base de datos (solo lectura),
grafica el resultado y redacta un análisis. Además: tableros guardables,
exportación a PDF/Excel e informes automáticos por correo.

## Arquitectura

```
Navegador ──> nginx (Angular) ──/api──> FastAPI ──┬─ PostgreSQL local  (usuarios, chats, tableros)
                                                  └─ Supabase          (datos del call center, solo lectura)
```

| Carpeta | Qué es |
|---|---|
| `backend/` | API en FastAPI (Python 3.12): auth JWT, motor NL→SQL con OpenAI, informes, exportación |
| `frontend/` | SPA en Angular 21 (standalone + signals), servida por nginx |
| `db/` | Esquema inicial de la base del aplicativo |

## Cómo levantarlo

Requisitos: **Docker Desktop**.

```bash
docker compose up -d
```

Luego abrir **http://localhost:8095**

| Perfil | Usuario | Contraseña |
|---|---|---|
| Admin | admin@estadiscall.com | Estadis.Admin.2026 |
| Supervisor | supervisor@estadiscall.com | Estadis.Super.2026 |
| Coordinador | coordinador@estadiscall.com | Estadis.Coord.2026 |
| Financiero | financiero@estadiscall.com | Estadis.Finanzas.2026 |

> Son las credenciales de demostración que crea el sistema la primera vez.
> Cámbialas desde *Usuarios* si el despliegue es real.

## Configuración de las integraciones

Al entrar por primera vez, ir a **Configuración** (solo admin) y cargar:

- **Supabase** — host, usuario y contraseña de la base con los datos del call center
- **OpenAI** — API key para el chat de IA
- **SMTP** — cuenta de correo para los informes programados

Estos datos **no viven en archivos**: se guardan cifrados (Fernet) en la base
del aplicativo. Por eso el repositorio no contiene ninguna credencial.

## Funcionalidades

- **Consultar IA** — pregunta libre en español; si es ambigua, el sistema pide
  aclaraciones (período, tipo de gráfico) antes de responder
- **Tableros** — guarda cualquier resultado como widget; 4 tableros vienen precargados
- **Informes** — programa el envío diario de un tablero en PDF por correo
- **Usuarios** — gestión por perfiles (admin, supervisor, coordinador, financiero)
- **Exportación** — PDF (con el gráfico incrustado) y Excel

## Notas de seguridad

- El SQL que genera la IA pasa por un validador (`sqlguard.py`) que solo permite
  `SELECT`/`WITH` y fuerza un límite de filas.
- Los widgets de tablero se ejecutan por identificador, nunca enviando SQL desde
  el cliente.
- El login tiene límite de intentos (5/min por IP) contra fuerza bruta.
- Se recomienda conectar Supabase con un **usuario de solo lectura**, no con el
  administrador de la base.

## Desarrollo

Frontend con recarga en caliente (requiere el backend levantado):

```bash
npm start --prefix frontend
```

Queda en http://localhost:4200 y redirige `/api` al backend automáticamente.
