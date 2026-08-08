import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';

import { Fila } from '../../../../shared/models/consulta.model';
import { Campania } from '../../../../shared/models/panel.model';
import { ExportService } from '../../../../shared/services/export.service';
import { PanelService } from '../../../../shared/services/panel.service';
import { mensajeError } from '../../../../shared/utils/errores';

const COLUMNAS_EXCEL = [
  'codigo',
  'nombre',
  'tipo_campania',
  'llamadas',
  'contestadas',
  'pct_contacto',
  'ventas',
  'monto_ventas',
  'costo_total',
];

@Component({
  selector: 'app-campanias-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './campanias-page.html',
  styleUrl: './campanias-page.scss',
})
export class CampaniasPage {
  private readonly panel = inject(PanelService);
  private readonly exportar = inject(ExportService);

  protected readonly campanias = signal<Campania[]>([]);
  protected readonly cargando = signal(true);
  protected readonly error = signal('');

  protected readonly activas = computed(
    () => this.campanias().filter((c) => c.estado === 'activa').length,
  );

  protected progresoPct(c: Campania): number {
    if (!c.meta_llamadas_dia) return 0;
    return Math.min(100, Math.round((c.llamadas / c.meta_llamadas_dia) * 100));
  }

  protected colorProgreso(c: Campania): 'green' | 'amber' | 'red' {
    const pct = this.progresoPct(c);
    if (pct >= 100) return 'green';
    if (pct >= 50) return 'amber';
    return 'red';
  }

  protected exportarExcel(): void {
    const filas = this.campanias() as unknown as Fila[];
    this.exportar
      .excel({ titulo: 'Campañas', columnas: COLUMNAS_EXCEL, filas }, 'campanias.xlsx')
      .subscribe();
  }

  constructor() {
    this.panel.campanias().subscribe({
      next: (d) => {
        this.campanias.set(d.campanias);
        this.cargando.set(false);
      },
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudieron cargar las campañas'));
        this.cargando.set(false);
      },
    });
  }
}
