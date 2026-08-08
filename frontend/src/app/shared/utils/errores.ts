import { HttpErrorResponse } from '@angular/common/http';

/**
 * FastAPI devuelve siempre { detail: "..." } en los errores (ver los
 * HTTPException de backend/app/routers/*.py). Cuando la validación de
 * Pydantic falla, detail es una lista de objetos en vez de un string.
 */
export function mensajeError(err: unknown, respaldo = 'Ocurrió un error'): string {
  if (err instanceof HttpErrorResponse) {
    const detail = err.error?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length) {
      return detail.map((d) => d?.msg ?? '').filter(Boolean).join(' · ') || respaldo;
    }
    if (err.status === 0) {
      return 'No se pudo contactar al servidor.';
    }
  }
  return respaldo;
}
