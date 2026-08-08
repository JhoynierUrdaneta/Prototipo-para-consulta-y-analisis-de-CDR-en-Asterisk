import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  Dashboard,
  DashboardActualizar,
  DashboardCrear,
  Widget,
} from '../models/dashboard.model';

/** backend/app/routers/dashboards.py */
@Injectable({ providedIn: 'root' })
export class DashboardsService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/dashboards`;

  /** Devuelve los propios y los compartidos por otros. */
  listar(): Observable<Dashboard[]> {
    return this.http.get<Dashboard[]>(this.base);
  }

  obtener(id: string): Observable<Dashboard> {
    return this.http.get<Dashboard>(`${this.base}/${id}`);
  }

  crear(body: DashboardCrear): Observable<Dashboard> {
    return this.http.post<Dashboard>(this.base, body);
  }

  /** Crea el tablero sugerido según el perfil del usuario. */
  crearDesdePlantilla(): Observable<Dashboard> {
    return this.http.post<Dashboard>(`${this.base}/plantilla`, {});
  }

  actualizar(id: string, body: DashboardActualizar): Observable<Dashboard> {
    return this.http.patch<Dashboard>(`${this.base}/${id}`, body);
  }

  agregarWidget(id: string, widget: Widget): Observable<Dashboard> {
    return this.http.post<Dashboard>(`${this.base}/${id}/widgets`, widget);
  }

  eliminar(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
