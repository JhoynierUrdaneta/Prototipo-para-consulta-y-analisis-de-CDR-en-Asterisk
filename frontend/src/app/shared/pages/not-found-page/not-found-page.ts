import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found-page',
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="wrap">
      <div class="code">404</div>
      <h1>Esta página no existe</h1>
      <p>Puede que el enlace esté roto o que la sección se haya movido.</p>
      <a class="btn btn-primary" routerLink="/app">Volver al panel</a>
    </div>
  `,
  styles: `
    .wrap {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 10px;
      background: var(--sidebar-bg);
      text-align: center;
      padding: 24px;
    }
    .code {
      font-family: var(--mono);
      font-size: 64px;
      font-weight: 700;
      color: var(--sidebar-act-t);
    }
    h1 {
      font-size: 20px;
      color: #f1f5f9;
    }
    p {
      font-size: 13px;
      color: #64748b;
      margin-bottom: 10px;
    }
  `,
})
export class NotFoundPage {}
