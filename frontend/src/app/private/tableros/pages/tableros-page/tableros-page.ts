import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { Dashboard } from '../../../../shared/models/dashboard.model';
import { DashboardsService } from '../../../../shared/services/dashboards.service';
import { mensajeError } from '../../../../shared/utils/errores';

type Filtro = 'todos' | 'mios' | 'compartidos';

@Component({
  selector: 'app-tableros-page',
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './tableros-page.html',
  styleUrl: './tableros-page.scss',
})
export class TablerosPage {
  private readonly dashboards = inject(DashboardsService);
  private readonly router = inject(Router);

  protected readonly lista = signal<Dashboard[]>([]);
  protected readonly filtro = signal<Filtro>('todos');
  protected readonly cargando = signal(true);
  protected readonly error = signal('');

  protected readonly mios = computed(() => this.lista().filter((d) => d.es_propio));
  protected readonly compartidos = computed(() => this.lista().filter((d) => !d.es_propio));

  protected readonly visibles = computed(() => {
    switch (this.filtro()) {
      case 'mios':
        return this.mios();
      case 'compartidos':
        return this.compartidos();
      default:
        return this.lista();
    }
  });

  constructor() {
    this.cargar();
  }

  protected crearDesdePlantilla(): void {
    this.dashboards.crearDesdePlantilla().subscribe({
      next: (d) => void this.router.navigate(['/app/tableros', d.id]),
      error: (err: unknown) => this.error.set(mensajeError(err, 'No se pudo crear el tablero')),
    });
  }

  protected eliminar(d: Dashboard, evento: Event): void {
    // La tarjeta entera es un enlace al detalle: aquí no queremos navegar.
    evento.preventDefault();
    evento.stopPropagation();
    if (!confirm(`¿Eliminar el tablero "${d.nombre}"?`)) {
      return;
    }
    this.dashboards.eliminar(d.id).subscribe({
      next: () => this.cargar(),
      error: (err: unknown) => this.error.set(mensajeError(err, 'No se pudo eliminar')),
    });
  }

  private cargar(): void {
    this.cargando.set(true);
    this.dashboards.listar().subscribe({
      next: (ds) => {
        this.lista.set(ds);
        this.cargando.set(false);
      },
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudieron cargar los tableros'));
        this.cargando.set(false);
      },
    });
  }
}
