import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Conversacion, MensajeConversacion } from '../models/consulta.model';

/** backend/app/routers/conversaciones.py — historial de chat (retención 30 días). */
@Injectable({ providedIn: 'root' })
export class ConversacionesService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/conversaciones`;

  listar(): Observable<Conversacion[]> {
    return this.http.get<Conversacion[]>(this.base);
  }

  mensajes(id: string): Observable<MensajeConversacion[]> {
    return this.http.get<MensajeConversacion[]>(`${this.base}/${id}/mensajes`);
  }

  eliminar(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
