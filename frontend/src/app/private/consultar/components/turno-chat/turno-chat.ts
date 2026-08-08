import { ChangeDetectionStrategy, Component, computed, inject, input, output, signal, viewChild } from '@angular/core';

import { Grafico } from '../../../../shared/components/grafico/grafico';
import { Widget } from '../../../../shared/models/dashboard.model';
import { ExportService } from '../../../../shared/services/export.service';
import type { Turno } from '../../pages/consultar-page/consultar-page';
import { FormAclaracion } from '../form-aclaracion/form-aclaracion';
import { GuardarTableroModal } from '../guardar-tablero-modal/guardar-tablero-modal';

/** Un turno del chat: la burbuja del usuario y la tarjeta de respuesta. */
@Component({
  selector: 'app-turno-chat',
  imports: [Grafico, FormAclaracion, GuardarTableroModal],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './turno-chat.html',
  styleUrl: './turno-chat.scss',
})
export class TurnoChat {
  private readonly exportar = inject(ExportService);

  readonly turno = input.required<Turno>();
  readonly aclarar = output<Record<string, string>>();

  private readonly grafico = viewChild(Grafico);

  protected readonly verSql = signal(false);
  protected readonly mostrarGuardar = signal(false);

  /** Lo que se guarda como widget en un tablero. */
  protected readonly widget = computed<Widget>(() => {
    const d = this.turno().data!;
    return {
      titulo: d.titulo,
      sql: d.sql,
      tipo_grafico: d.tipo_grafico,
      eje_x: d.eje_x,
      series: d.series,
      insight: d.insight,
    };
  });

  protected exportarPdf(): void {
    const d = this.turno().data;
    if (!d) {
      return;
    }
    this.exportar
      .pdf(
        {
          titulo: d.titulo,
          insight: d.insight,
          recomendaciones: d.recomendaciones,
          columnas: d.columnas,
          filas: d.filas,
          // Sin esto el PDF sale sin la imagen del gráfico.
          chart_png: this.grafico()?.getPng(),
        },
        `${d.titulo}.pdf`,
      )
      .subscribe();
  }

  protected exportarExcel(): void {
    const d = this.turno().data;
    if (!d) {
      return;
    }
    this.exportar
      .excel({ titulo: d.titulo, columnas: d.columnas, filas: d.filas }, `${d.titulo}.xlsx`)
      .subscribe();
  }
}
