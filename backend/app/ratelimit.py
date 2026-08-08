import time
from collections import defaultdict, deque

from fastapi import HTTPException, status

_hits: dict[str, deque] = defaultdict(deque)


_MENSAJE_POR_DEFECTO = "Demasiadas consultas seguidas. Espera un momento."


def limit(key: str, max_req: int, window_seg: float, mensaje: str | None = None) -> None:
    """Rate limit por clave con ventana deslizante en memoria. Lanza 429 si se excede.

    NOTA: es in-memory por proceso; si se escala a varias réplicas, mover a Redis.
    """
    now = time.monotonic()
    dq = _hits[key]
    while dq and now - dq[0] > window_seg:
        dq.popleft()
    if len(dq) >= max_req:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, mensaje or _MENSAJE_POR_DEFECTO
        )
    dq.append(now)
