import { Routes } from '@angular/router';

import { authGuard } from './shared/guards/auth.guard';

export const routes: Routes = [
  {
    path: 'auth',
    loadChildren: () => import('./auth/auth.routes').then((m) => m.authRoutes),
  },
  {
    path: 'app',
    canActivate: [authGuard],
    loadChildren: () => import('./private/private.routes').then((m) => m.privateRoutes),
  },
  {
    path: '404',
    loadComponent: () =>
      import('./shared/pages/not-found-page/not-found-page').then((m) => m.NotFoundPage),
  },
  { path: '', pathMatch: 'full', redirectTo: 'app' },
  { path: '**', redirectTo: '404' },
];
