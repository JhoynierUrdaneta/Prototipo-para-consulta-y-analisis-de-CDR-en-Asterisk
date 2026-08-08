import { ChangeDetectionStrategy, Component, inject, input, output, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { Dashboard } from '../../../../shared/models/dashboard.model';
import { Frecuencia, Informe } from '../../../../shared/models/informe.model';
import { InformesService } from '../../../../shared/services/informes.service';
import { mensajeError } from '../../../../shared/utils/errores';

@Component({
  selector: 'app-informe-form-modal',
  imports: [ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './informe-form-modal.html',
})
export class InformeFormModal {
  private readonly fb = inject(FormBuilder);
  private readonly informes = inject(InformesService);

  /** Si viene un informe se edita; si no, se crea uno nuevo. */
  readonly informe = input<Informe | null>(null);
  readonly tableros = input.required<Dashboard[]>();
  readonly cerrar = output<void>();
  readonly guardado = output<void>();

  protected readonly enviando = signal(false);
  protected readonly error = signal('');

  protected readonly form = this.fb.nonNullable.group({
    nombre: ['', Validators.required],
    dashboard_id: ['', Validators.required],
    destinatarios: ['', Validators.required],
    hora: ['08:00', [Validators.required, Validators.pattern(/^\d{2}:\d{2}$/)]],
    frecuencia: ['diario' as Frecuencia, Validators.required],
  });

  constructor() {
    const actual = this.informe();
    if (actual) {
      this.form.patchValue({
        nombre: actual.nombre,
        dashboard_id: actual.dashboard_id ?? '',
        destinatarios: actual.destinatarios,
        hora: actual.hora,
        frecuencia: actual.frecuencia,
      });
      // El backend no permite mover un informe a otro tablero.
      this.form.controls.dashboard_id.disable();
    }
  }

  protected enviar(): void {
    if (this.form.invalid || this.enviando()) {
      this.form.markAllAsTouched();
      return;
    }
    this.enviando.set(true);
    this.error.set('');

    const v = this.form.getRawValue();
    const actual = this.informe();
    const peticion = actual
      ? this.informes.actualizar(actual.id, {
          nombre: v.nombre,
          destinatarios: v.destinatarios,
          hora: v.hora,
          frecuencia: v.frecuencia,
        })
      : this.informes.crear(v);

    peticion.subscribe({
      next: () => this.guardado.emit(),
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudo guardar el informe'));
        this.enviando.set(false);
      },
    });
  }
}
