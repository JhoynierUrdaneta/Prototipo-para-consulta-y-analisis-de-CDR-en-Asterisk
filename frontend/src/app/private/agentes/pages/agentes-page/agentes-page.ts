import { DecimalPipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';

import { Agente, AgentesRespuesta } from '../../../../shared/models/panel.model';
import { PanelService } from '../../../../shared/services/panel.service';
import { colorEstadoAgente, grupoEstadoAgente } from '../../../../shared/utils/estados';
import { mensajeError } from '../../../../shared/utils/errores';

const GRUPOS = ['Disponible', 'En llamada', 'En pausa', 'Capacitación/reunión', 'Desconectado'] as const;

/** Paleta cíclica para los avatares, determinada por el código del agente
 * (mismo agente = mismo color siempre, sin depender de un campo del backend). */
const DEGRADADOS = [
  'linear-gradient(135deg,#0ea5e9,#0284c7)',
  'linear-gradient(135deg,#8b5cf6,#6d28d9)',
  'linear-gradient(135deg,#f59e0b,#d97706)',
  'linear-gradient(135deg,#10b981,#059669)',
  'linear-gradient(135deg,#06b6d4,#0891b2)',
  'linear-gradient(135deg,#ef4444,#dc2626)',
];

function degradado(codigo: string): string {
  const n = codigo.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
  return DEGRADADOS[n % DEGRADADOS.length]!;
}

function iniciales(a: Agente): string {
  return ((a.nombres[0] ?? '') + (a.apellidos[0] ?? '')).toUpperCase();
}

@Component({
  selector: 'app-agentes-page',
  imports: [DecimalPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './agentes-page.html',
  styleUrl: './agentes-page.scss',
})
export class AgentesPage {
  private readonly panel = inject(PanelService);

  protected readonly datos = signal<AgentesRespuesta | null>(null);
  protected readonly cargando = signal(true);
  protected readonly error = signal('');

  protected readonly filtroGrupo = signal<string | null>(null);
  protected readonly filtroCampania = signal<string | null>(null);

  protected readonly colorEstadoAgente = colorEstadoAgente;
  protected readonly degradado = degradado;
  protected readonly iniciales = iniciales;

  protected readonly agentes = computed(() => this.datos()?.agentes ?? []);

  /** Conteo por grupo, para los chips ("Disponible (4)") y el subtítulo. */
  protected readonly conteoPorGrupo = computed(() => {
    const mapa = new Map<string, number>();
    for (const a of this.agentes()) {
      const g = grupoEstadoAgente(a.estado_codigo);
      mapa.set(g, (mapa.get(g) ?? 0) + 1);
    }
    return mapa;
  });

  protected readonly campanias = computed(() => {
    const set = new Set<string>();
    for (const a of this.agentes()) {
      if (a.campania_codigo) set.add(a.campania_codigo);
    }
    return [...set].sort();
  });

  protected readonly grupos = GRUPOS;

  protected readonly agentesFiltrados = computed(() => {
    const grupo = this.filtroGrupo();
    const campania = this.filtroCampania();
    return this.agentes().filter((a) => {
      if (grupo && grupoEstadoAgente(a.estado_codigo) !== grupo) return false;
      if (campania && a.campania_codigo !== campania) return false;
      return true;
    });
  });

  protected grupoElegido(a: Agente): string {
    return grupoEstadoAgente(a.estado_codigo);
  }

  protected elegirGrupo(g: string | null): void {
    this.filtroGrupo.set(this.filtroGrupo() === g ? null : g);
  }

  protected elegirCampania(c: string | null): void {
    this.filtroCampania.set(this.filtroCampania() === c ? null : c);
  }

  constructor() {
    this.panel.agentes().subscribe({
      next: (d) => {
        this.datos.set(d);
        this.cargando.set(false);
      },
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudieron cargar los agentes'));
        this.cargando.set(false);
      },
    });
  }
}
