import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';

import { OpenAIEstado, OpenAIGuardar } from '../../../../shared/models/config.model';
import { ConfigService } from '../../../../shared/services/config.service';
import { mensajeError } from '../../../../shared/utils/errores';

@Component({
  selector: 'app-openai-card',
  imports: [ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './openai-card.html',
})
export class OpenaiCard {
  private readonly fb = inject(FormBuilder);
  private readonly config = inject(ConfigService);

  protected readonly estado = signal<OpenAIEstado | null>(null);
  protected readonly ocupado = signal<'guardar' | 'probar' | null>(null);
  protected readonly ok = signal('');
  protected readonly error = signal('');

  protected readonly form = this.fb.nonNullable.group({
    api_key: [''],
    model: ['gpt-4o'],
    base_url: [''],
  });

  constructor() {
    this.config.obtenerOpenai().subscribe((e) => {
      this.estado.set(e);
      this.form.patchValue({ model: e.model, base_url: e.base_url ?? '' });
    });
  }

  /** La API key solo viaja si el usuario escribió una nueva. */
  private cuerpo(): OpenAIGuardar {
    const v = this.form.getRawValue();
    return {
      model: v.model,
      ...(v.api_key ? { api_key: v.api_key } : {}),
      ...(v.base_url ? { base_url: v.base_url } : {}),
    };
  }

  protected guardar(): void {
    this.iniciar('guardar');
    this.config.guardarOpenai(this.cuerpo()).subscribe({
      next: () => {
        this.ok.set('Configuración guardada y cifrada.');
        this.form.controls.api_key.reset('');
        this.recargar();
      },
      error: (err: unknown) => this.fallo(err),
    });
  }

  protected probar(): void {
    this.iniciar('probar');
    this.config.probarOpenai(this.cuerpo()).subscribe({
      next: (r) => {
        this.ok.set(`Conexión exitosa · ${r.modelos_disponibles} modelos disponibles.`);
        this.ocupado.set(null);
      },
      error: (err: unknown) => this.fallo(err),
    });
  }

  private iniciar(accion: 'guardar' | 'probar'): void {
    this.ocupado.set(accion);
    this.ok.set('');
    this.error.set('');
  }

  private fallo(err: unknown): void {
    this.error.set(mensajeError(err, 'Falló la operación'));
    this.ocupado.set(null);
  }

  private recargar(): void {
    this.config.obtenerOpenai().subscribe((e) => {
      this.estado.set(e);
      this.ocupado.set(null);
    });
  }
}
