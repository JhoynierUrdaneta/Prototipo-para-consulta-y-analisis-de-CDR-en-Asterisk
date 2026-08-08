// Espejo de WidgetSpec / DashboardIn / DashboardUpdate en schemas.py.
export interface Widget {
  titulo: string;
  sql: string;
  tipo_grafico: string;
  eje_x?: string | null;
  series?: string[];
  descripcion?: string | null;
  insight?: string | null;
}

export interface Dashboard {
  id: string;
  nombre: string;
  definicion: Widget[];
  compartido: boolean;
  es_propio: boolean;
}

export interface DashboardCrear {
  nombre: string;
  definicion: Widget[];
}

export interface DashboardActualizar {
  nombre?: string;
  definicion?: Widget[];
  compartido?: boolean;
}
