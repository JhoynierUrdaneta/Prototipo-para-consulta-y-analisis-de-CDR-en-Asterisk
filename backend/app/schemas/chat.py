from pydantic import BaseModel
from typing import Optional, List, Any


class ChatRequest(BaseModel):
    pregunta: str

    class Config:
        json_schema_extra = {
            "example": {
                "pregunta": "¿Cuántas llamadas contestadas hubo hoy?"
            }
        }


class ChatResponse(BaseModel):
    pregunta: str
    respuesta: str
    sql_generado: Optional[str] = None
    datos: Optional[List[Any]] = []
