import { DatePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  computed,
  inject,
  signal,
  viewChild,
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  Conversacion,
  PreguntaAclaracion,
  ResultadoConsulta,
  esAclaracion,
} from '../../../../shared/models/consulta.model';
import { ConsultaService } from '../../../../shared/services/consulta.service';
import { ConversacionesService } from '../../../../shared/services/conversaciones.service';
import { mensajeError } from '../../../../shared/utils/errores';
import { TurnoChat } from '../../components/turno-chat/turno-chat';

/** Un intercambio del chat: la pregunta y lo que respondió el backend. */
export interface Turno {
  pregunta: string;
  cargando: boolean;
  error?: string;
  aclaracion?: PreguntaAclaracion[];
  data?: ResultadoConsulta;
}

const SUGERENCIAS = [
  'Top 5 campañas con más ventas hoy',
  'Costo total por destino hoy',
  'Distribución de llamadas por estado',
  'Agentes con mejor contactabilidad',
];

@Component({
  selector: 'app-consultar-page',
  imports: [FormsModule, DatePipe, TurnoChat],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './consultar-page.html',
  styleUrl: './consultar-page.scss',
})
export class ConsultarPage {
  private readonly consultas = inject(ConsultaService);
  private readonly conversaciones = inject(ConversacionesService);

  private readonly fin = viewChild<ElementRef<HTMLElement>>('fin');

  protected readonly sugerencias = SUGERENCIAS;
  protected readonly turnos = signal<Turno[]>([]);
  protected readonly lista = signal<Conversacion[]>([]);
  protected readonly conversacionId = signal<string | null>(null);
  protected readonly ocupado = signal(false);
  protected texto = '';

  /** Modo "seleccionar varias" del historial, para borrar en lote. */
  protected readonly modoSeleccion = signal(false);
  protected readonly seleccionadas = signal<ReadonlySet<string>>(new Set());
  protected readonly borrando = signal(false);

  protected readonly todasSeleccionadas = computed(
    () => this.lista().length > 0 && this.seleccionadas().size === this.lista().length,
  );

  constructor() {
    // Al entrar, restaura la última conversación para no perder el hilo
    // al cambiar de sección (mismo comportamiento que el React).
    this.conversaciones.listar().subscribe((convs) => {
      this.lista.set(convs);
      if (convs.length) {
        this.abrir(convs[0]!.id);
      }
    });
  }

  protected abrir(id: string): void {
    this.conversaciones.mensajes(id).subscribe((mensajes) => {
      const turnos: Turno[] = [];
      for (const m of mensajes) {
        if (m.rol === 'user') {
          turnos.push({ pregunta: m.contenido ?? '', cargando: false });
        } else if (turnos.length && m.datos) {
          turnos[turnos.length - 1]!.data = m.datos;
        }
      }
      this.turnos.set(turnos);
      this.conversacionId.set(id);
      this.irAlFinal();
    });
  }

  protected nueva(): void {
    this.turnos.set([]);
    this.conversacionId.set(null);
  }

  protected cambiarConversacion(id: string): void {
    if (id) {
      this.abrir(id);
    } else {
      this.nueva();
    }
  }

  protected borrarConversacion(): void {
    const id = this.conversacionId();
    if (!id || !confirm('¿Eliminar esta conversación?')) {
      return;
    }
    this.conversaciones.eliminar(id).subscribe(() => {
      this.nueva();
      this.recargarLista();
    });
  }

  protected activarSeleccion(): void {
    this.modoSeleccion.set(true);
    this.seleccionadas.set(new Set());
  }

  protected cancelarSeleccion(): void {
    this.modoSeleccion.set(false);
    this.seleccionadas.set(new Set());
  }

  /** En modo selección el clic marca/desmarca en vez de abrir la conversación. */
  protected alPulsarItem(id: string): void {
    if (this.modoSeleccion()) {
      this.alternarSeleccion(id);
    } else {
      this.abrir(id);
    }
  }

  protected alternarSeleccion(id: string): void {
    this.seleccionadas.update((actuales) => {
      const copia = new Set(actuales);
      if (!copia.delete(id)) {
        copia.add(id);
      }
      return copia;
    });
  }

  protected alternarTodas(): void {
    this.seleccionadas.set(
      this.todasSeleccionadas() ? new Set() : new Set(this.lista().map((c) => c.id)),
    );
  }

  protected borrarSeleccionadas(): void {
    const ids = [...this.seleccionadas()];
    if (ids.length === 0 || this.borrando()) {
      return;
    }
    const mensaje =
      ids.length === 1
        ? '¿Eliminar esta conversación?'
        : `¿Eliminar ${ids.length} conversaciones? Esta acción no se puede deshacer.`;
    if (!confirm(mensaje)) {
      return;
    }

    this.borrando.set(true);
    const abierta = this.conversacionId();
    this.conversaciones.eliminarVarias(ids).subscribe({
      next: () => {
        // Si la conversación abierta se fue en el lote, se limpia el panel.
        if (abierta && ids.includes(abierta)) {
          this.nueva();
        }
        this.cancelarSeleccion();
        this.borrando.set(false);
        this.recargarLista();
      },
      error: () => this.borrando.set(false),
    });
  }

  protected enviar(): void {
    const pregunta = this.texto.trim();
    if (pregunta) {
      this.texto = '';
      this.preguntar(pregunta);
    }
  }

  protected preguntar(pregunta: string, aclaraciones?: Record<string, string>, indice?: number): void {
    if (!pregunta.trim() || this.ocupado()) {
      return;
    }
    this.ocupado.set(true);

    // Una aclaración reutiliza su turno; una pregunta nueva añade uno.
    const i = indice ?? this.turnos().length;
    if (indice === undefined) {
      this.turnos.update((t) => [...t, { pregunta, cargando: true }]);
    } else {
      this.actualizarTurno(i, { cargando: true, aclaracion: undefined, error: undefined });
    }
    this.irAlFinal();

    this.consultas.preguntar(pregunta, this.conversacionId(), aclaraciones).subscribe({
      next: (res) => {
        if (esAclaracion(res)) {
          this.actualizarTurno(i, { cargando: false, aclaracion: res.preguntas });
        } else {
          this.actualizarTurno(i, { cargando: false, data: res });
          if (res.conversacion_id) {
            this.conversacionId.set(res.conversacion_id);
            this.recargarLista();
          }
        }
        this.terminar();
      },
      error: (err: unknown) => {
        this.actualizarTurno(i, { cargando: false, error: mensajeError(err) });
        this.terminar();
      },
    });
  }

  protected responderAclaracion(indice: number, respuestas: Record<string, string>): void {
    this.preguntar(this.turnos()[indice]!.pregunta, respuestas, indice);
  }

  private actualizarTurno(indice: number, cambios: Partial<Turno>): void {
    this.turnos.update((t) => t.map((x, i) => (i === indice ? { ...x, ...cambios } : x)));
  }

  private terminar(): void {
    this.ocupado.set(false);
    this.irAlFinal();
  }

  private recargarLista(): void {
    this.conversaciones.listar().subscribe((convs) => this.lista.set(convs));
  }

  /** El DOM aún no reflejó el cambio de señal: se aplaza un tick. */
  private irAlFinal(): void {
    setTimeout(() => this.fin()?.nativeElement.scrollIntoView({ behavior: 'smooth' }), 60);
  }
}
