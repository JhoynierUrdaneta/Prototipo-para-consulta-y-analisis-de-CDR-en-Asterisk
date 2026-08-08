import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

interface Caracteristica {
  icono: string;
  titulo: string;
  texto: string;
}

@Component({
  selector: 'app-auth-layout',
  imports: [RouterOutlet],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './auth-layout.html',
  styleUrl: './auth-layout.scss',
})
export class AuthLayout {
  protected readonly caracteristicas: Caracteristica[] = [
    { icono: '🤖', titulo: 'Chat con IA', texto: 'Consulta métricas en español sin saber SQL' },
    { icono: '📊', titulo: 'Dashboards vivos', texto: 'KPIs por campaña y agente en tiempo real' },
    { icono: '💰', titulo: 'Control financiero', texto: 'Costo, margen y ROI por campaña y agente' },
    { icono: '📄', titulo: 'Exportación', texto: 'Reportes en PDF o Excel con un clic' },
  ];
}
