import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { CloudflareEstado } from '../../../../shared/models/config.model';
import { ConfigService } from '../../../../shared/services/config.service';
import { mensajeError } from '../../../../shared/utils/errores';

@Component({
  selector: 'app-cloudflare-card',
  imports: [FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './cloudflare-card.html',
})
export class CloudflareCard {
  private readonly config = inject(ConfigService);

  protected readonly estado = signal<CloudflareEstado | null>(null);
  protected readonly ocupado = signal(false);
  protected readonly ok = signal('');
  protected readonly error = signal('');

  protected token = '';

  constructor() {
    this.recargar();
  }

  protected guardar(): void {
    if (!this.token || this.ocupado()) {
      return;
    }
    this.iniciar();
    this.config.guardarCloudflare(this.token).subscribe({
      next: () => {
        this.ok.set('Token guardado. El túnel se activará en unos segundos.');
        this.token = '';
        this.recargar();
      },
      error: (err: unknown) => this.fallo(err),
    });
  }

  protected detener(): void {
    if (!confirm('¿Detener la publicación por Cloudflare?')) {
      return;
    }
    this.iniciar();
    this.config.eliminarCloudflare().subscribe({
      next: () => {
        this.ok.set('Túnel detenido.');
        this.recargar();
      },
      error: (err: unknown) => this.fallo(err),
    });
  }

  private iniciar(): void {
    this.ocupado.set(true);
    this.ok.set('');
    this.error.set('');
  }

  private fallo(err: unknown): void {
    this.error.set(mensajeError(err, 'Falló la operación'));
    this.ocupado.set(false);
  }

  private recargar(): void {
    this.config.obtenerCloudflare().subscribe((e) => {
      this.estado.set(e);
      this.ocupado.set(false);
    });
  }
}
