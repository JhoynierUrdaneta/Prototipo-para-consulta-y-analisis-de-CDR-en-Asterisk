import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';

import { TokenStore } from '../services/token.store';

/** Añade el Bearer a toda petición saliente (equivale al interceptor de axios del React). */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(TokenStore).leer();
  if (!token) {
    return next(req);
  }
  return next(req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
};
