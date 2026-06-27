from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

app = FastAPI(
    title="CDR VoIP API",
    description="API para consulta y análisis de registros CDR con IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

@app.get("/")
def root():
    return {"mensaje": "API CDR VoIP funcionando correctamente"}

@app.get("/cdr")
async def get_cdr():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/cdr?order=calldate.desc&limit=100",
                headers=get_headers()
            )
            return {"data": response.json(), "total": len(response.json())}
    except Exception as e:
        return {"error": str(e)}

@app.get("/cdr/stats")
async def get_stats():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/cdr?select=disposition,billsec",
                headers=get_headers()
            )
            data = response.json()
            total = len(data)
            contestadas = len([r for r in data if r.get("disposition") == "ANSWERED"])
            no_contestadas = len([r for r in data if r.get("disposition") == "NO ANSWER"])
            ocupadas = len([r for r in data if r.get("disposition") == "BUSY"])
            duracion_promedio = round(
                sum(r.get("billsec", 0) for r in data) / total if total > 0 else 0, 2
            )
            return {
                "total_llamadas": total,
                "contestadas": contestadas,
                "no_contestadas": no_contestadas,
                "ocupadas": ocupadas,
                "duracion_promedio": duracion_promedio
            }
    except Exception as e:
        return {"error": str(e)}