import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, of, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { LoginOut, Perfil, Usuario } from '../models/usuario.model';
import { TokenStore } from './token.store';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly tokens = inject(TokenStore);
  private readonly base = `${environment.apiUrl}/auth`;

  private readonly _usuario = signal<Usuario | null>(null);

  readonly usuario = this._usuario.asReadonly();
  readonly estaAutenticado = computed(() => this._usuario() !== null);
  readonly perfil = computed<Perfil | null>(() => this._usuario()?.perfil ?? null);

  /** Iniciales para el avatar del sidebar: "Andry Sierra" -> "AS". */
  readonly iniciales = computed(() => {
    const nombre = this._usuario()?.nombre ?? '';
    return nombre
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0]!.toUpperCase())
      .join('');
  });

  login(correo: string, password: string): Observable<LoginOut> {
    return this.http.post<LoginOut>(`${this.base}/login`, { correo, password }).pipe(
      tap((r) => {
        this.tokens.guardar(r.token);
        this._usuario.set(r.usuario);
      }),
    );
  }

  /**
   * Rehidrata la sesión al arrancar la app. Nunca propaga error: si el token
   * está vencido o es inválido se limpia y la app arranca deslogueada.
   */
  cargarUsuario(): Observable<Usuario | null> {
    if (!this.tokens.leer()) {
      return of(null);
    }
    return this.http.get<Usuario>(`${this.base}/me`).pipe(
      tap((u) => this._usuario.set(u)),
      catchError(() => {
        this.limpiarSesion();
        return of(null);
      }),
    );
  }

  logout(): void {
    this.limpiarSesion();
    void this.router.navigate(['/auth/login']);
  }

  limpiarSesion(): void {
    this.tokens.borrar();
    this._usuario.set(null);
  }

  tienePerfil(roles: readonly Perfil[]): boolean {
    const perfil = this.perfil();
    return perfil !== null && roles.includes(perfil);
  }
}
