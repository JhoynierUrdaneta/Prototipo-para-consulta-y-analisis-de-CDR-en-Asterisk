import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Usuario, UsuarioActualizar, UsuarioCrear } from '../models/usuario.model';

/** backend/app/routers/usuarios.py (todo el router exige perfil admin). */
@Injectable({ providedIn: 'root' })
export class UsuariosService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/usuarios`;

  listar(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(this.base);
  }

  crear(body: UsuarioCrear): Observable<Usuario> {
    return this.http.post<Usuario>(this.base, body);
  }

  actualizar(id: string, body: UsuarioActualizar): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.base}/${id}`, body);
  }

  /** Baja lógica: el backend marca activo = false para conservar el histórico. */
  desactivar(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
