// Espejo de backend/app/panel.py y routers/panel.py.

export interface ResumenHoy {
  llamadas_hoy: number;
  contestadas: number;
  ventas: number;
  monto_ventas: number;
  costo_total: number;
  campanias_activas: number;
  agentes_con_actividad: number;
}

export interface CampaniaKpi {
  campania_codigo: string;
  campania: string;
  llamadas: number;
  contestadas: number;
  pct_contacto: number;
  ventas: number;
  costo_total: number;
  estado: string;
}

export interface EstadoAgentesGrupo {
  estado: string;
  total: number;
}

export interface DisposicionItem {
  estado_llamada: string;
  total: number;
}

export interface ResumenOperativo {
  resumen: ResumenHoy;
  campanias: CampaniaKpi[];
  estado_agentes: EstadoAgentesGrupo[];
  disposicion: DisposicionItem[];
}

export interface Agente {
  id: number;
  codigo_agente: string;
  nombres: string;
  apellidos: string;
  equipo: string | null;
  campania_codigo: string | null;
  estado_codigo: string;
  estado: string;
  llamadas: number;
  ventas: number;
  tmo_seg: number | null;
}

export interface TopAgenteVenta {
  agente: string;
  codigo_agente: string;
  equipo: string;
  llamadas: number;
  ventas: number;
  tmo_seg: number;
}

export interface AgentesRespuesta {
  agentes: Agente[];
  top_ventas: TopAgenteVenta[];
}

export interface Campania {
  id: number;
  codigo: string;
  nombre: string;
  modalidad: string;
  meta_llamadas_dia: number;
  tipo_campania: string;
  llamadas: number;
  contestadas: number;
  pct_contacto: number;
  ventas: number;
  pct_conversion: number;
  monto_ventas: number;
  costo_total: number;
  tmo_seg: number;
  estado: string;
}

export interface CampaniasRespuesta {
  campanias: Campania[];
}
