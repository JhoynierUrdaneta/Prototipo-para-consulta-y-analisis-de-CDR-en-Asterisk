import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { Perfil } from '../../../shared/models/usuario.model';
import { AuthService } from '../../../shared/services/auth.service';

interface ItemNav {
  ruta: string;
  etiqueta: string;
  icono: string;
  /** Si se omite, el ítem es visible para todos los perfiles. */
  roles?: Perfil[];
  /** Marca "exact" en routerLinkActive (solo para la raíz). */
  exacto?: boolean;
  insignia?: string;
}

interface GrupoNav {
  titulo: string;
  items: ItemNav[];
}

@Component({
  selector: 'app-private-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './private-layout.html',
  styleUrl: './private-layout.scss',
})
export class PrivateLayout {
  private readonly auth = inject(AuthService);

  protected readonly usuario = this.auth.usuario;
  protected readonly iniciales = this.auth.iniciales;

  // Los ítems Agentes / Campañas / Financiero del diseño llegarán cuando el
  // backend exponga endpoints sobre v_kpi_agente_dia y v_kpi_campania_dia.
  private readonly grupos: GrupoNav[] = [
    {
      titulo: 'Principal',
      items: [
        { ruta: '/app', etiqueta: 'Panel', icono: '📊', exacto: true },
        { ruta: '/app/consultar', etiqueta: 'Consultar IA', icono: '🤖', insignia: 'IA' },
        { ruta: '/app/tableros', etiqueta: 'Tableros', icono: '🗂️' },
      ],
    },
    {
      titulo: 'Sistema',
      items: [
        { ruta: '/app/informes', etiqueta: 'Informes', icono: '📧' },
        { ruta: '/app/usuarios', etiqueta: 'Usuarios', icono: '👥', roles: ['admin'] },
        { ruta: '/app/configuracion', etiqueta: 'Configuración', icono: '⚙️', roles: ['admin'] },
      ],
    },
  ];

  /** Grupos filtrados por el perfil, sin dejar grupos vacíos. */
  protected readonly navegacion = computed(() => {
    const perfil = this.auth.perfil();
    return this.grupos
      .map((g) => ({
        ...g,
        items: g.items.filter((i) => !i.roles || (perfil !== null && i.roles.includes(perfil))),
      }))
      .filter((g) => g.items.length > 0);
  });

  protected cerrarSesion(): void {
    this.auth.logout();
  }
}
