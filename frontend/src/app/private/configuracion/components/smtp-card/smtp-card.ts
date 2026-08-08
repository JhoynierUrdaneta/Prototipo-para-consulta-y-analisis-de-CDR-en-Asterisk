import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { SmtpEstado, SmtpGuardar } from '../../../../shared/models/config.model';
import { ConfigService } from '../../../../shared/services/config.service';
import { mensajeError } from '../../../../shared/utils/errores';

@Component({
  selector: 'app-smtp-card',
  imports: [ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './smtp-card.html',
})
export class SmtpCard {
  private readonly fb = inject(FormBuilder);
  private readonly config = inject(ConfigService);

  protected readonly estado = signal<SmtpEstado | null>(null);
  protected readonly ocupado = signal<'guardar' | 'probar' | null>(null);
  protected readonly ok = signal('');
  protected readonly error = signal('');

  protected readonly form = this.fb.nonNullable.group({
    host: ['', Validators.required],
    port: [587, Validators.required],
    user: ['', Validators.required],
    password: [''],
    from_email: [''],
    use_tls: [true],
  });

  constructor() {
    this.config.obtenerSmtp().subscribe((e) => {
      this.estado.set(e);
      this.form.patchValue({
        host: e.host ?? '',
        port: e.port,
        user: e.user ?? '',
        from_email: e.from_email ?? '',
        use_tls: e.use_tls,
      });
    });
  }

  private cuerpo(): SmtpGuardar {
    const v = this.form.getRawValue();
    return {
      host: v.host,
      port: Number(v.port),
      user: v.user,
      use_tls: v.use_tls,
      ...(v.password ? { password: v.password } : {}),
      ...(v.from_email ? { from_email: v.from_email } : {}),
    };
  }

  protected guardar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.iniciar('guardar');
    this.config.guardarSmtp(this.cuerpo()).subscribe({
      next: () => {
        this.ok.set('Configuración guardada y cifrada.');
        this.form.controls.password.reset('');
        this.recargar();
      },
      error: (err: unknown) => this.fallo(err),
    });
  }

  protected probar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.iniciar('probar');
    this.config.probarSmtp(this.cuerpo()).subscribe({
      next: () => {
        this.ok.set('Conexión SMTP exitosa.');
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
    this.config.obtenerSmtp().subscribe((e) => {
      this.estado.set(e);
      this.ocupado.set(null);
    });
  }
}
