import httpx
from app.core.config import SUPABASE_URL, get_headers


async def fetch(endpoint: str, params: str = "") -> list | dict:
    """Hace un GET a la API REST de Supabase y retorna el JSON"""
    async with httpx.AsyncClient() as client:
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        if params:
            url += f"?{params}"
        response = await client.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json()
