import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';

import { CampaniaKpi, ResumenOperativo } from '../../../../shared/models/panel.model';
import { Perfil } from '../../../../shared/models/usuario.model';
import { AuthService } from '../../../../shared/services/auth.service';
import { PanelService } from '../../../../shared/services/panel.service';
import { colorEstadoAgente, colorEstadoLlamada, etiquetaEstadoLlamada } from '../../../../shared/utils/estados';
import { formatearValor } from '../../../../shared/utils/formato';
import { mensajeError } from '../../../../shared/utils/errores';

const SALUDO: Record<Perfil, string> = {
  admin: 'Tienes control total: usuarios, integraciones y toda la operación.',
  supervisor: 'Consulta el desempeño de tus campañas y agentes en tiempo real.',
  coordinador: 'Visión transversal de la operación y sus indicadores.',
  financiero: 'Sigue costos, ingresos y rentabilidad de la operación.',
};

interface KpiCard {
  icono: string;
  label: string;
  valor: string;
  color: 'blue' | 'green' | 'amber' | 'purple';
}

/** Dashboard operativo — reemplaza al antiguo Panel de bienvenida estático. */
@Component({
  selector: 'app-panel-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './panel-page.html',
  styleUrl: './panel-page.scss',
})
export class PanelPage {
  private readonly auth = inject(AuthService);
  private readonly panel = inject(PanelService);

  protected readonly usuario = this.auth.usuario;
  protected readonly saludo = computed(() => {
    const perfil = this.auth.perfil();
    return perfil ? SALUDO[perfil] : '';
  });

  protected readonly datos = signal<ResumenOperativo | null>(null);
  protected readonly cargando = signal(true);
  protected readonly error = signal('');

  protected readonly Math = Math;
  protected readonly colorEstadoAgente = colorEstadoAgente;
  protected readonly colorEstadoLlamada = colorEstadoLlamada;
  protected readonly etiquetaEstadoLlamada = etiquetaEstadoLlamada;
  protected readonly fmt = formatearValor;

  protected readonly kpis = computed<KpiCard[]>(() => {
    const r = this.datos()?.resumen;
    if (!r) return [];
    return [
      { icono: '📞', label: 'Total llamadas', valor: this.fmt(r.llamadas_hoy), color: 'blue' },
      { icono: '✅', label: 'Contestadas', valor: this.fmt(r.contestadas), color: 'green' },
      { icono: '🏆', label: 'Ventas cerradas', valor: this.fmt(r.ventas), color: 'amber' },
      { icono: '💰', label: 'Costo total', valor: '$' + this.fmt(Math.round(r.costo_total)), color: 'purple' },
    ];
  });

  /** Máximo de llamadas entre campañas, para dimensionar las barras del "Estado agentes". */
  protected readonly maxEstadoAgentes = computed(() => {
    const items = this.datos()?.estado_agentes ?? [];
    return Math.max(1, ...items.map((i) => i.total));
  });

  protected readonly totalDisposicion = computed(() =>
    (this.datos()?.disposicion ?? []).reduce((acc, d) => acc + d.total, 0),
  );

  protected pctDisposicion(total: number): number {
    const t = this.totalDisposicion();
    return t > 0 ? Math.round((total / t) * 100) : 0;
  }

  protected trackCampania(_i: number, c: CampaniaKpi): string {
    return c.campania_codigo;
  }

  constructor() {
    this.panel.resumen().subscribe({
      next: (d) => {
        this.datos.set(d);
        this.cargando.set(false);
      },
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudo cargar el resumen operativo'));
        this.cargando.set(false);
      },
    });
  }
}
