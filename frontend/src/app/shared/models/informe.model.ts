// Espejo de InformeIn / InformeUpdate en schemas.py y de la tabla
// informes_programados (backend/app/migrate.py).
export type Frecuencia = 'diario' | 'habiles';

export interface Informe {
  id: string;
  nombre: string;
  dashboard_id: string | null;
  /** Correos separados por coma. */
  destinatarios: string;
  /** HH:MM en hora Colombia. */
  hora: string;
  frecuencia: Frecuencia;
  activo: boolean;
  ultimo_envio: string | null;
}

export interface InformeCrear {
  nombre: string;
  dashboard_id: string;
  destinatarios: string;
  hora: string;
  frecuencia: Frecuencia;
}

export interface InformeActualizar {
  nombre?: string;
  destinatarios?: string;
  hora?: string;
  frecuencia?: Frecuencia;
  activo?: boolean;
}
