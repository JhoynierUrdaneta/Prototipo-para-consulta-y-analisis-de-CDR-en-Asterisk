import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { FilasSql, RespuestaConsulta } from '../models/consulta.model';

/** backend/app/routers/consulta.py */
@Injectable({ providedIn: 'root' })
export class ConsultaService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/consulta`;

  /**
   * Pregunta en lenguaje natural. Puede responder con el reporte ya resuelto
   * o con hasta 3 preguntas de aclaración; se reenvía con `aclaraciones`.
   */
  preguntar(
    pregunta: string,
    conversacionId: string | null,
    aclaraciones?: Record<string, string>,
  ): Observable<RespuestaConsulta> {
    return this.http.post<RespuestaConsulta>(this.base, {
      pregunta,
      conversacion_id: conversacionId,
      aclaraciones: aclaraciones ?? null,
    });
  }

  /**
   * Ejecuta el SQL guardado de un widget. Se envía qué widget es, no la
   * consulta: el SQL lo resuelve el backend para que el cliente no pueda
   * ejecutar SELECTs arbitrarios.
   */
  ejecutarWidget(dashboardId: string, widgetIndex: number): Observable<FilasSql> {
    return this.http.post<FilasSql>(`${this.base}/ejecutar`, {
      dashboard_id: dashboardId,
      widget_index: widgetIndex,
    });
  }

  /** Consola SQL sin IA (solo admin). */
  ejecutarSql(sql: string): Observable<FilasSql> {
    return this.http.post<FilasSql>(`${this.base}/sql`, { sql });
  }

  esquema(): Observable<{ esquema: string }> {
    return this.http.get<{ esquema: string }>(`${this.base}/esquema`);
  }
}
