import { Injectable } from '@angular/core';

/**
 * Única fuente de verdad para la clave del token en localStorage.
 * La usan AuthService y authInterceptor; tenerla aparte evita que el
 * interceptor tenga que inyectar AuthService (que a su vez usa HttpClient).
 */
@Injectable({ providedIn: 'root' })
export class TokenStore {
  private static readonly CLAVE = 'token';

  leer(): string | null {
    return localStorage.getItem(TokenStore.CLAVE);
  }

  guardar(token: string): void {
    localStorage.setItem(TokenStore.CLAVE, token);
  }

  borrar(): void {
    localStorage.removeItem(TokenStore.CLAVE);
  }
}
