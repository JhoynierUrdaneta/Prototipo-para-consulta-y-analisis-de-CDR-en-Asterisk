import { Routes } from '@angular/router';

import { rolGuard } from '../shared/guards/auth.guard';
import { PrivateLayout } from './layout/private-layout/private-layout';

export const privateRoutes: Routes = [
  {
    path: '',
    component: PrivateLayout,
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./panel/pages/panel-page/panel-page').then((m) => m.PanelPage),
      },
      {
        path: 'agentes',
        loadComponent: () =>
          import('./agentes/pages/agentes-page/agentes-page').then((m) => m.AgentesPage),
      },
      {
        path: 'campanias',
        loadComponent: () =>
          import('./campanias/pages/campanias-page/campanias-page').then((m) => m.CampaniasPage),
      },
      {
        path: 'consultar',
        loadComponent: () =>
          import('./consultar/pages/consultar-page/consultar-page').then((m) => m.ConsultarPage),
      },
      {
        path: 'tableros',
        loadComponent: () =>
          import('./tableros/pages/tableros-page/tableros-page').then((m) => m.TablerosPage),
      },
      {
        path: 'tableros/:id',
        loadComponent: () =>
          import('./tableros/pages/tablero-detalle-page/tablero-detalle-page').then(
            (m) => m.TableroDetallePage,
          ),
      },
      {
        path: 'informes',
        loadComponent: () =>
          import('./informes/pages/informes-page/informes-page').then((m) => m.InformesPage),
      },
      {
        path: 'usuarios',
        canActivate: [rolGuard('admin')],
        loadComponent: () =>
          import('./usuarios/pages/usuarios-page/usuarios-page').then((m) => m.UsuariosPage),
      },
      {
        path: 'configuracion',
        canActivate: [rolGuard('admin')],
        loadComponent: () =>
          import('./configuracion/pages/configuracion-page/configuracion-page').then(
            (m) => m.ConfiguracionPage,
          ),
      },
      { path: '**', redirectTo: '' },
    ],
  },
];
