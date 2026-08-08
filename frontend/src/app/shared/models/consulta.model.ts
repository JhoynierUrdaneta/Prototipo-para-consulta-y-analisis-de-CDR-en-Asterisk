// Respuestas de POST /api/consulta (backend/app/nlsql.py -> responder()).
export type TipoGrafico = 'number' | 'bar' | 'line' | 'area' | 'pie' | 'table';

export type Fila = Record<string, unknown>;

/** Lo mínimo que el componente Grafico necesita para pintar. */
export interface Resultado {
  titulo: string;
  tipo_grafico: string;
  eje_x: string | null;
  series: string[];
  columnas: string[];
  filas: Fila[];
}

/** Respuesta completa de una consulta resuelta. */
export interface ResultadoConsulta extends Resultado {
  tipo: 'resultado';
  pregunta: string;
  sql: string;
  resumen: string;
  descripcion: string;
  insight: string;
  recomendaciones: string[];
  ms: number;
  n_filas: number;
  conversacion_id?: string;
}

export interface PreguntaAclaracion {
  pregunta: string;
  clave: string;
  opciones: string[];
}

export interface RespuestaAclaracion {
  tipo: 'aclaracion';
  preguntas: PreguntaAclaracion[];
}

export type RespuestaConsulta = ResultadoConsulta | RespuestaAclaracion;

export function esAclaracion(r: RespuestaConsulta): r is RespuestaAclaracion {
  return r.tipo === 'aclaracion';
}

export interface ConsultaIn {
  pregunta: string;
  conversacion_id?: string | null;
  aclaraciones?: Record<string, string> | null;
}

/** Respuesta de /api/consulta/ejecutar y /api/consulta/sql. */
export interface FilasSql {
  columnas: string[];
  filas: Fila[];
  n_filas: number;
  ms?: number;
}

export interface Conversacion {
  id: string;
  titulo: string;
  created_at: string;
}

export interface MensajeConversacion {
  rol: 'user' | 'assistant';
  contenido: string | null;
  datos: ResultadoConsulta | null;
}
