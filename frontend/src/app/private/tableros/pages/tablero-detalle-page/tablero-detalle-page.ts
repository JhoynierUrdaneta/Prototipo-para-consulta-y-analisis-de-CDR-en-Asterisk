import { ChangeDetectionStrategy, Component, effect, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { Dashboard } from '../../../../shared/models/dashboard.model';
import { DashboardsService } from '../../../../shared/services/dashboards.service';
import { mensajeError } from '../../../../shared/utils/errores';
import { WidgetCard } from '../../components/widget-card/widget-card';

@Component({
  selector: 'app-tablero-detalle-page',
  imports: [RouterLink, WidgetCard],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './tablero-detalle-page.html',
  styleUrl: './tablero-detalle-page.scss',
})
export class TableroDetallePage {
  private readonly dashboards = inject(DashboardsService);

  /** Llega del parámetro de ruta gracias a withComponentInputBinding(). */
  readonly id = input.required<string>();

  protected readonly tablero = signal<Dashboard | null>(null);
  protected readonly error = signal('');

  constructor() {
    effect(() => {
      this.dashboards.obtener(this.id()).subscribe({
        next: (d) => this.tablero.set(d),
        error: (err: unknown) =>
          this.error.set(mensajeError(err, 'No se encontró el tablero')),
      });
    });
  }
}
