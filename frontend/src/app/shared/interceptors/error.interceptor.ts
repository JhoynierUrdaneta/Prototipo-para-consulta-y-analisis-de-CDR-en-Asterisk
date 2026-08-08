import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { TokenStore } from '../services/token.store';

// El login responde 401 con credenciales malas: ahí el 401 es la respuesta
// esperada, no una sesión vencida. /auth/me lo maneja AuthService.cargarUsuario(),
// que arranca la app deslogueada sin necesidad de redirigir.
const SIN_REDIRECCION = ['/auth/login', '/auth/me'];

/** Ante un 401 de sesión vencida: limpia el token y manda al login. */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const tokens = inject(TokenStore);
  const router = inject(Router);

  return next(req).pipe(
    catchError((err: unknown) => {
      const esSesionVencida =
        err instanceof HttpErrorResponse &&
        err.status === 401 &&
        !SIN_REDIRECCION.some((ruta) => req.url.includes(ruta));

      if (esSesionVencida) {
        tokens.borrar();
        void router.navigate(['/auth/login']);
      }
      return throwError(() => err);
    }),
  );
};
