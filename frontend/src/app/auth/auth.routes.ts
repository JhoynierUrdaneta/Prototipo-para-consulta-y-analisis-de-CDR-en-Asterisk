import { Routes } from '@angular/router';

import { AuthLayout } from './layout/auth-layout/auth-layout';

export const authRoutes: Routes = [
  {
    path: '',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        loadComponent: () => import('./pages/login-page/login-page').then((m) => m.LoginPage),
      },
      { path: '**', redirectTo: 'login' },
    ],
  },
];
