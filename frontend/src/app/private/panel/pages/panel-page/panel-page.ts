import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';

import { Perfil } from '../../../../shared/models/usuario.model';
import { AuthService } from '../../../../shared/services/auth.service';

const SALUDO: Record<Perfil, string> = {
  admin: 'Tienes control total: usuarios, integraciones y toda la operación.',
  supervisor: 'Consulta el desempeño de tus campañas y agentes en tiempo real.',
  coordinador: 'Visión transversal de la operación y sus indicadores.',
  financiero: 'Sigue costos, ingresos y rentabilidad de la operación.',
};

@Component({
  selector: 'app-panel-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './panel-page.html',
  styleUrl: './panel-page.scss',
})
export class PanelPage {
  private readonly auth = inject(AuthService);

  protected readonly usuario = this.auth.usuario;
  protected readonly saludo = computed(() => {
    const perfil = this.auth.perfil();
    return perfil ? SALUDO[perfil] : '';
  });
}
