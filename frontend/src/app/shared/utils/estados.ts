/**
 * Colores para los estados de agente y de llamada. Centralizado porque lo
 * usan tanto el Dashboard como la pantalla de Agentes.
 */

export type ColorPill = 'green' | 'blue' | 'amber' | 'purple' | 'red' | 'gray';

const COLOR_ESTADO_AGENTE: Record<string, ColorPill> = {
  Disponible: 'green',
  'En llamada': 'blue',
  'En pausa': 'amber',
  'Capacitación/reunión': 'purple',
  'Capacitación': 'purple',
  Desconectado: 'gray',
};

export function colorEstadoAgente(estado: string): ColorPill {
  return COLOR_ESTADO_AGENTE[estado] ?? 'gray';
}

// Mismo agrupamiento que backend/app/panel.py::estado_agentes_resumen(), pero
// por código (DISPONIBLE, EN_LLAMADA...) para poder filtrar/colorear cada
// tarjeta de agente sin perder el detalle de su estado real.
const GRUPO_POR_CODIGO: Record<string, string> = {
  DISPONIBLE: 'Disponible',
  EN_LLAMADA: 'En llamada',
  ACW: 'En llamada',
  PAUSA_BANIO: 'En pausa',
  PAUSA_ALMUERZO: 'En pausa',
  PAUSA_DESCANSO: 'En pausa',
  CAPACITACION: 'Capacitación/reunión',
  REUNION: 'Capacitación/reunión',
  DESCONECTADO: 'Desconectado',
};

export function grupoEstadoAgente(estadoCodigo: string): string {
  return GRUPO_POR_CODIGO[estadoCodigo] ?? 'Desconectado';
}

const COLOR_ESTADO_LLAMADA: Record<string, ColorPill> = {
  contestada: 'green',
  no_contesta: 'amber',
  ocupado: 'red',
  abandonada: 'purple',
  buzon: 'blue',
  fallida: 'gray',
};

const ETIQUETA_ESTADO_LLAMADA: Record<string, string> = {
  contestada: 'Contestada',
  no_contesta: 'No contesta',
  ocupado: 'Ocupado',
  abandonada: 'Abandonada',
  buzon: 'Buzón',
  fallida: 'Fallida',
};

export function colorEstadoLlamada(estado: string): ColorPill {
  return COLOR_ESTADO_LLAMADA[estado] ?? 'gray';
}

export function etiquetaEstadoLlamada(estado: string): string {
  return ETIQUETA_ESTADO_LLAMADA[estado] ?? estado;
}
