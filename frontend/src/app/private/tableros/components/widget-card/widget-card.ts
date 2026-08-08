import { ChangeDetectionStrategy, Component, effect, inject, input, signal, viewChild } from '@angular/core';

import { Grafico } from '../../../../shared/components/grafico/grafico';
import { Resultado } from '../../../../shared/models/consulta.model';
import { Widget } from '../../../../shared/models/dashboard.model';
import { ConsultaService } from '../../../../shared/services/consulta.service';
import { ExportService } from '../../../../shared/services/export.service';
import { mensajeError } from '../../../../shared/utils/errores';

/** Ejecuta el SQL guardado del widget y lo pinta. */
@Component({
  selector: 'app-widget-card',
  imports: [Grafico],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './widget-card.html',
  styleUrl: './widget-card.scss',
})
export class WidgetCard {
  private readonly consultas = inject(ConsultaService);
  private readonly exportar = inject(ExportService);

  readonly widget = input.required<Widget>();
  /** El backend resuelve el SQL a partir de estos dos datos. */
  readonly dashboardId = input.required<string>();
  readonly indice = input.required<number>();

  private readonly grafico = viewChild(Grafico);

  protected readonly resultado = signal<Resultado | null>(null);
  protected readonly error = signal('');

  constructor() {
    effect(() => {
      const w = this.widget();
      this.resultado.set(null);
      this.error.set('');

      this.consultas.ejecutarWidget(this.dashboardId(), this.indice()).subscribe({
        next: (r) =>
          this.resultado.set({
            titulo: w.titulo,
            tipo_grafico: w.tipo_grafico,
            eje_x: w.eje_x ?? null,
            series: w.series ?? [],
            columnas: r.columnas,
            filas: r.filas,
          }),
        error: (err: unknown) => this.error.set(mensajeError(err, 'No se pudo cargar el widget')),
      });
    });
  }

  protected exportarPdf(): void {
    const r = this.resultado();
    if (!r) {
      return;
    }
    this.exportar
      .pdf(
        {
          titulo: r.titulo,
          insight: this.widget().insight,
          columnas: r.columnas,
          filas: r.filas,
          chart_png: this.grafico()?.getPng(),
        },
        `${r.titulo}.pdf`,
      )
      .subscribe();
  }
}
