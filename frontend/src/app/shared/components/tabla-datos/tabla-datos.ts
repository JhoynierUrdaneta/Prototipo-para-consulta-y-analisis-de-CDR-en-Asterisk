import { ChangeDetectionStrategy, Component, input } from '@angular/core';

import { Fila } from '../../models/consulta.model';
import { formatearValor } from '../../utils/formato';

/** Tabla de resultados reutilizable (chat, widgets y bajo las tortas). */
@Component({
  selector: 'app-tabla-datos',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="contenedor">
      <table class="tbl">
        <thead>
          <tr>
            @for (c of columnas(); track c) {
              <th>{{ c }}</th>
            }
          </tr>
        </thead>
        <tbody>
          @for (f of filas(); track $index) {
            <tr>
              @for (c of columnas(); track c) {
                <td>{{ formatear(f[c]) }}</td>
              }
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
  styles: `
    .contenedor {
      overflow-x: auto;
      overflow-y: auto;
      max-height: 360px;
      border: 1px solid var(--border);
      border-radius: 8px;
    }
  `,
})
export class TablaDatos {
  readonly columnas = input.required<string[]>();
  readonly filas = input.required<Fila[]>();

  protected readonly formatear = formatearValor;
}
