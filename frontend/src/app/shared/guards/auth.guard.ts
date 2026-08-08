import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { Perfil } from '../models/usuario.model';
import { AuthService } from '../services/auth.service';

/** Exige sesión iniciada. La sesión ya viene rehidratada por el appInitializer. */
export const authGuard: CanActivateFn = (_ruta, estado) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.estaAutenticado()) {
    return true;
  }
  // returnUrl para volver a donde iba después de iniciar sesión.
  return router.createUrlTree(['/auth/login'], {
    queryParams: { returnUrl: estado.url },
  });
};

/** Exige uno de los perfiles indicados; si no, devuelve al panel. */
export function rolGuard(...roles: Perfil[]): CanActivateFn {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    return auth.tienePerfil(roles) ? true : router.createUrlTree(['/app']);
  };
}
