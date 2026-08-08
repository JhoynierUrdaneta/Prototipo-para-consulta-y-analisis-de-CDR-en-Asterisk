import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Informe, InformeActualizar, InformeCrear } from '../models/informe.model';

/** backend/app/routers/informes.py — informes programados por correo. */
@Injectable({ providedIn: 'root' })
export class InformesService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/informes`;

  listar(): Observable<Informe[]> {
    return this.http.get<Informe[]>(this.base);
  }

  crear(body: InformeCrear): Observable<Informe> {
    return this.http.post<Informe>(this.base, body);
  }

  actualizar(id: string, body: InformeActualizar): Observable<Informe> {
    return this.http.patch<Informe>(`${this.base}/${id}`, body);
  }

  eliminar(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }

  /** Genera el PDF del tablero y lo envía ya. Requiere SMTP configurado. */
  enviarAhora(id: string): Observable<{ ok: boolean }> {
    return this.http.post<{ ok: boolean }>(`${this.base}/${id}/enviar`, {});
  }
}
