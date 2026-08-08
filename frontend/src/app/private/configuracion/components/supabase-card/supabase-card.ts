import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { SupabaseEstado, SupabaseGuardar } from '../../../../shared/models/config.model';
import { ConfigService } from '../../../../shared/services/config.service';
import { mensajeError } from '../../../../shared/utils/errores';

@Component({
  selector: 'app-supabase-card',
  imports: [ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './supabase-card.html',
})
export class SupabaseCard {
  private readonly fb = inject(FormBuilder);
  private readonly config = inject(ConfigService);

  protected readonly estado = signal<SupabaseEstado | null>(null);
  protected readonly ocupado = signal<'guardar' | 'probar' | null>(null);
  protected readonly ok = signal('');
  protected readonly error = signal('');

  protected readonly form = this.fb.nonNullable.group({
    url: [''],
    db_host: ['', Validators.required],
    db_port: [5432, Validators.required],
    db_name: ['postgres', Validators.required],
    db_user: ['', Validators.required],
    db_password: [''],
    anon_key: [''],
  });

  constructor() {
    this.config.obtenerSupabase().subscribe((e) => {
      this.estado.set(e);
      this.form.patchValue({
        url: e.url ?? '',
        db_host: e.db_host ?? '',
        db_port: e.db_port,
        db_name: e.db_name,
        db_user: e.db_user ?? '',
      });
    });
  }

  private cuerpo(): SupabaseGuardar {
    const v = this.form.getRawValue();
    return {
      db_host: v.db_host,
      db_port: Number(v.db_port),
      db_name: v.db_name,
      db_user: v.db_user,
      ...(v.url ? { url: v.url } : {}),
      ...(v.db_password ? { db_password: v.db_password } : {}),
      ...(v.anon_key ? { anon_key: v.anon_key } : {}),
    };
  }

  protected guardar(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.iniciar('guardar');
    this.config.guardarSupabase(this.cuerpo()).subscribe({
      next: () => {
        this.ok.set('Configuración guardada y cifrada.');
        this.form.controls.db_password.reset('');
        this.form.controls.anon_key.reset('');
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
    this.config.probarSupabase(this.cuerpo()).subscribe({
      next: (r) => {
        this.ok.set(
          `Conexión exitosa · PostgreSQL ${r.server_version} · ${r.tablas_public} tablas.`,
        );
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
    this.config.obtenerSupabase().subscribe((e) => {
      this.estado.set(e);
      this.ocupado.set(null);
    });
  }
}
