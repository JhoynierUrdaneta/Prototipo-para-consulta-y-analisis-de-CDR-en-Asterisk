import { registerLocaleData } from '@angular/common';
import localeEsCo from '@angular/common/locales/es-CO';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import {
  ApplicationConfig,
  LOCALE_ID,
  inject,
  provideAppInitializer,
  provideBrowserGlobalErrorListeners,
} from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideEchartsCore } from 'ngx-echarts';

import { routes } from './app.routes';
import { authInterceptor } from './shared/interceptors/auth.interceptor';
import { errorInterceptor } from './shared/interceptors/error.interceptor';
import { AuthService } from './shared/services/auth.service';

// Los importes de moneda y miles del call center son colombianos.
registerLocaleData(localeEsCo);

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
    provideEchartsCore({ echarts: () => import('echarts') }),
    { provide: LOCALE_ID, useValue: 'es-CO' },

    // Rehidrata la sesión antes de renderizar la primera ruta: sin esto,
    // recargar con F5 en una ruta privada rebotaría al login por un instante.
    provideAppInitializer(() => inject(AuthService).cargarUsuario()),
  ],
};
