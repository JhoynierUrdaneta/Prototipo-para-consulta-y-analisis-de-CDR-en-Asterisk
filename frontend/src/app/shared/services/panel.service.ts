import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  AgentesRespuesta,
  CampaniasRespuesta,
  ResumenOperativo,
} from '../models/panel.model';

/** backend/app/routers/panel.py — KPIs operativos de solo lectura sobre Supabase. */
@Injectable({ providedIn: 'root' })
export class PanelService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/panel`;

  resumen(): Observable<ResumenOperativo> {
    return this.http.get<ResumenOperativo>(`${this.base}/resumen`);
  }

  agentes(): Observable<AgentesRespuesta> {
    return this.http.get<AgentesRespuesta>(`${this.base}/agentes`);
  }

  campanias(): Observable<CampaniasRespuesta> {
    return this.http.get<CampaniasRespuesta>(`${this.base}/campanias`);
  }
}
