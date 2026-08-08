import { ChangeDetectionStrategy, Component, inject, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { Dashboard, Widget } from '../../../../shared/models/dashboard.model';
import { DashboardsService } from '../../../../shared/services/dashboards.service';
import { mensajeError } from '../../../../shared/utils/errores';

/** Guarda el resultado del chat como widget: en un tablero nuevo o en uno existente. */
@Component({
  selector: 'app-guardar-tablero-modal',
  imports: [FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './guardar-tablero-modal.html',
})
export class GuardarTableroModal {
  private readonly dashboards = inject(DashboardsService);

  readonly widget = input.required<Widget>();
  readonly cerrar = output<void>();

  protected readonly propios = signal<Dashboard[]>([]);
  protected readonly guardando = signal(false);
  protected readonly error = signal('');
  protected readonly ok = signal(false);

  protected seleccion = 'nuevo';
  protected nombre = 'Mi tablero';

  constructor() {
    // Solo se puede añadir widgets a tableros propios.
    this.dashboards
      .listar()
      .subscribe((ds) => this.propios.set(ds.filter((d) => d.es_propio)));
  }

  protected guardar(): void {
    if (this.guardando()) {
      return;
    }
    this.guardando.set(true);
    this.error.set('');

    const peticion =
      this.seleccion === 'nuevo'
        ? this.dashboards.crear({ nombre: this.nombre, definicion: [this.widget()] })
        : this.dashboards.agregarWidget(this.seleccion, this.widget());

    peticion.subscribe({
      next: () => {
        this.ok.set(true);
        setTimeout(() => this.cerrar.emit(), 700);
      },
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudo guardar'));
        this.guardando.set(false);
      },
    });
  }
}
