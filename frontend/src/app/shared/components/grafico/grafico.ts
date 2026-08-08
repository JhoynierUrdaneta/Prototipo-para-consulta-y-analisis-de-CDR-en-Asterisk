import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import type { ECharts, EChartsCoreOption } from 'echarts/core';
import { NgxEchartsDirective } from 'ngx-echarts';

import { Resultado } from '../../models/consulta.model';
import { aNumero, formatearValor } from '../../utils/formato';
import { TablaDatos } from '../tabla-datos/tabla-datos';

const PALETA = ['#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#0284c7', '#94a3b8'];
const EJE = '#475569';
const GRID = '#e2e8f0';

/**
 * Pinta el resultado de una consulta. Portado de frontend/src/components/Grafico.tsx;
 * conserva sus tres reglas de negocio (ver comentarios en los computed).
 */
@Component({
  selector: 'app-grafico',
  imports: [NgxEchartsDirective, TablaDatos],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './grafico.html',
  styleUrl: './grafico.scss',
})
export class Grafico {
  readonly res = input.required<Resultado>();

  private instancia?: ECharts;

  protected readonly hayDatos = computed(() => this.res().filas.length > 0);

  /** Series declaradas por el planificador, o todas las columnas salvo el eje X. */
  protected readonly series = computed(() => {
    const { series, columnas, eje_x } = this.res();
    const base = series?.length ? series : columnas.filter((c) => c !== eje_x);
    return base.filter((c) => columnas.includes(c));
  });

  /**
   * Una torta solo representa UNA serie sobre categorías. Si hay varias
   * (comparativo entre entidades) no puede mostrarlo: se degrada a barras.
   */
  protected readonly tipoEfectivo = computed(() => {
    const tipo = this.res().tipo_grafico;
    return tipo === 'pie' && this.series().length > 1 ? 'bar' : tipo;
  });

  protected readonly esPie = computed(() => this.tipoEfectivo() === 'pie');

  /** Sin series numéricas no hay nada que graficar: se cae a tabla. */
  protected readonly esTabla = computed(
    () => this.tipoEfectivo() === 'table' || this.series().length === 0,
  );

  protected readonly esNumero = computed(() => this.res().tipo_grafico === 'number');

  /** Para el modo "number": la cifra grande y su etiqueta. */
  protected readonly columnaNumero = computed(() => {
    const { columnas } = this.res();
    return this.series()[0] ?? columnas[columnas.length - 1] ?? '';
  });

  protected readonly valorNumero = computed(() =>
    formatearValor(this.res().filas[0]?.[this.columnaNumero()]),
  );

  protected readonly opcion = computed<EChartsCoreOption>(() => {
    const { columnas, filas, eje_x } = this.res();
    const series = this.series();
    const tipo = this.tipoEfectivo();
    const columnaEje = eje_x ?? columnas[0]!;
    const categorias = filas.map((f) => formatearValor(f[columnaEje]));
    const tipoSerie = tipo === 'area' ? 'line' : tipo;

    return {
      color: PALETA,
      tooltip: { trigger: this.esPie() ? 'item' : 'axis' },
      legend: { textStyle: { color: EJE }, top: 0, icon: 'roundRect' },
      grid: { left: 8, right: 16, bottom: 8, top: 34, containLabel: true },
      xAxis: this.esPie()
        ? undefined
        : {
            type: 'category',
            data: categorias,
            axisLabel: { color: EJE },
            axisLine: { lineStyle: { color: GRID } },
          },
      yAxis: this.esPie()
        ? undefined
        : { type: 'value', axisLabel: { color: EJE }, splitLine: { lineStyle: { color: GRID } } },
      series: this.esPie()
        ? [
            {
              type: 'pie',
              radius: ['45%', '70%'],
              data: filas.map((f) => ({
                name: formatearValor(f[columnaEje]),
                value: aNumero(f[series[0]!]),
              })),
              label: { color: EJE },
            },
          ]
        : series.map((s) => ({
            name: s,
            type: tipoSerie,
            smooth: true,
            areaStyle: tipo === 'area' ? { opacity: 0.15 } : undefined,
            itemStyle: { borderRadius: tipoSerie === 'bar' ? [4, 4, 0, 0] : 0 },
            data: filas.map((f) => aNumero(f[s])),
          })),
    };
  });

  protected alIniciarChart(ec: ECharts): void {
    this.instancia = ec;
  }

  /**
   * PNG del gráfico para incrustarlo en el PDF (campo chart_png del backend).
   * Devuelve undefined si la vista actual no tiene chart (tabla o cifra).
   */
  getPng(): string | undefined {
    try {
      return this.instancia?.getDataURL({ pixelRatio: 2, backgroundColor: '#ffffff' });
    } catch {
      return undefined;
    }
  }
}
