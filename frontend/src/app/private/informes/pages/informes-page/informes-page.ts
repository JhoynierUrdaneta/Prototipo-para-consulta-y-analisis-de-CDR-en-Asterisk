import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';

import { Dashboard } from '../../../../shared/models/dashboard.model';
import { Informe } from '../../../../shared/models/informe.model';
import { DashboardsService } from '../../../../shared/services/dashboards.service';
import { InformesService } from '../../../../shared/services/informes.service';
import { mensajeError } from '../../../../shared/utils/errores';
import { InformeFormModal } from '../../components/informe-form-modal/informe-form-modal';

@Component({
  selector: 'app-informes-page',
  imports: [InformeFormModal],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './informes-page.html',
  styleUrl: './informes-page.scss',
})
export class InformesPage {
  private readonly informes = inject(InformesService);
  private readonly dashboards = inject(DashboardsService);

  protected readonly lista = signal<Informe[]>([]);
  protected readonly tableros = signal<Dashboard[]>([]);
  protected readonly cargando = signal(true);
  protected readonly error = signal('');
  protected readonly aviso = signal('');

  protected readonly modalAbierto = signal(false);
  protected readonly enEdicion = signal<Informe | null>(null);

  protected readonly activos = computed(() => this.lista().filter((i) => i.activo));

  /** Próximo envío = la hora más temprana entre los informes activos. */
  protected readonly proximoEnvio = computed(() => {
    const horas = this.activos()
      .map((i) => i.hora)
      .sort();
    return horas[0] ?? '—';
  });

  /** Destinatarios únicos en todas las listas. */
  protected readonly destinatarios = computed(() => {
    const correos = new Set<string>();
    for (const i of this.lista()) {
      for (const c of i.destinatarios.split(',')) {
        const limpio = c.trim().toLowerCase();
        if (limpio) {
          correos.add(limpio);
        }
      }
    }
    return correos.size;
  });

  constructor() {
    this.cargar();
    // Se necesitan para el selector del modal y para mostrar de qué tablero
    // sale cada informe.
    this.dashboards.listar().subscribe((ds) => this.tableros.set(ds));
  }

  protected nombreTablero(id: string | null): string {
    return this.tableros().find((t) => t.id === id)?.nombre ?? 'Tablero eliminado';
  }

  protected abrirNuevo(): void {
    this.enEdicion.set(null);
    this.modalAbierto.set(true);
  }

  protected abrirEdicion(i: Informe): void {
    this.enEdicion.set(i);
    this.modalAbierto.set(true);
  }

  protected alGuardar(): void {
    this.modalAbierto.set(false);
    this.cargar();
  }

  protected alternarActivo(i: Informe): void {
    this.informes.actualizar(i.id, { activo: !i.activo }).subscribe({
      next: () => this.cargar(),
      error: (err: unknown) => this.error.set(mensajeError(err)),
    });
  }

  protected enviarAhora(i: Informe): void {
    this.aviso.set('');
    this.error.set('');
    this.informes.enviarAhora(i.id).subscribe({
      next: () => this.aviso.set(`Informe "${i.nombre}" enviado.`),
      error: (err: unknown) => this.error.set(mensajeError(err, 'No se pudo enviar')),
    });
  }

  protected eliminar(i: Informe): void {
    if (!confirm(`¿Eliminar el informe "${i.nombre}"?`)) {
      return;
    }
    this.informes.eliminar(i.id).subscribe({
      next: () => this.cargar(),
      error: (err: unknown) => this.error.set(mensajeError(err)),
    });
  }

  private cargar(): void {
    this.cargando.set(true);
    this.informes.listar().subscribe({
      next: (is) => {
        this.lista.set(is);
        this.cargando.set(false);
      },
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudieron cargar los informes'));
        this.cargando.set(false);
      },
    });
  }
}
