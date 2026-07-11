from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chatbot con IA para consultas en lenguaje natural sobre los CDR.
    Recibe una pregunta en español y devuelve datos + descripción.
    
    Ejemplo de pregunta:
    - "¿Cuántas llamadas contestadas hubo hoy?"
    - "¿Cuál fue el agente con más ventas esta semana?"
    - "Muéstrame las llamadas abandonadas de la campaña VTA-MOVIL"
    
    TODO: Implementar integración con OpenAI en Sprint 4
    """
    return ChatResponse(
        pregunta=request.pregunta,
        respuesta="El módulo de IA estará disponible en el Sprint 4.",
        sql_generado=None,
        datos=[]
    )
