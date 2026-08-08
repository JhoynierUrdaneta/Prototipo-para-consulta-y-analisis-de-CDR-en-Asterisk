/**
 * Formato de celdas igual al del frontend React (fmt() en Grafico.tsx):
 * enteros con separador de miles, decimales a 2 cifras, resto tal cual.
 */
export function formatearValor(v: unknown): string {
  if (typeof v === 'number' && Number.isFinite(v)) {
    return Number.isInteger(v)
      ? v.toLocaleString('es-CO')
      : v.toLocaleString('es-CO', { maximumFractionDigits: 2 });
  }
  return v === null || v === undefined ? '' : String(v);
}

/** Convierte a número para las series del gráfico; lo no numérico vale 0. */
export function aNumero(v: unknown): number {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}
