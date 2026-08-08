import { ChangeDetectionStrategy, Component, computed, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { PreguntaAclaracion } from '../../../../shared/models/consulta.model';

/**
 * Cuando la pregunta es ambigua, el planificador devuelve hasta 3 preguntas
 * con opciones sugeridas (período, tipo de gráfico...). El usuario elige una
 * opción o escribe la suya.
 */
@Component({
  selector: 'app-form-aclaracion',
  imports: [FormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './form-aclaracion.html',
  styleUrl: './form-aclaracion.scss',
})
export class FormAclaracion {
  readonly preguntas = input.required<PreguntaAclaracion[]>();
  readonly responder = output<Record<string, string>>();

  protected readonly respuestas = signal<Record<string, string>>({});

  protected readonly completo = computed(() => {
    const r = this.respuestas();
    return this.preguntas().every((p) => !!r[p.clave]?.trim());
  });

  protected elegir(clave: string, valor: string): void {
    this.respuestas.update((r) => ({ ...r, [clave]: valor }));
  }

  protected estaElegida(p: PreguntaAclaracion, opcion: string): boolean {
    return this.respuestas()[p.clave] === opcion;
  }

  /** Lo escrito a mano solo se muestra si no coincide con ninguna opción. */
  protected valorLibre(p: PreguntaAclaracion): string {
    const valor = this.respuestas()[p.clave] ?? '';
    return p.opciones.includes(valor) ? '' : valor;
  }

  protected enviar(): void {
    if (this.completo()) {
      this.responder.emit(this.respuestas());
    }
  }
}
