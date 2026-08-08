import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Fila } from '../models/consulta.model';

export interface ExportarPdf {
  titulo: string;
  insight?: string | null;
  recomendaciones?: string[];
  columnas: string[];
  filas: Fila[];
  /** dataURL del gráfico (image/png;base64,...) que produce GraficoComponent.getPng(). */
  chart_png?: string;
}

export interface ExportarExcel {
  titulo: string;
  columnas: string[];
  filas: Fila[];
}

/** backend/app/routers/export.py — devuelve el archivo como blob. */
@Injectable({ providedIn: 'root' })
export class ExportService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/export`;

  pdf(body: ExportarPdf, nombreArchivo: string): Observable<Blob> {
    return this.descargar(`${this.base}/pdf`, body, nombreArchivo);
  }

  excel(body: ExportarExcel, nombreArchivo: string): Observable<Blob> {
    return this.descargar(`${this.base}/excel`, body, nombreArchivo);
  }

  private descargar(url: string, body: unknown, nombreArchivo: string): Observable<Blob> {
    return this.http
      .post(url, body, { responseType: 'blob' })
      .pipe(tap((blob) => this.dispararDescarga(blob, nombreArchivo)));
  }

  private dispararDescarga(blob: Blob, nombreArchivo: string): void {
    const href = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = href;
    a.download = nombreArchivo;
    a.click();
    URL.revokeObjectURL(href);
  }
}
