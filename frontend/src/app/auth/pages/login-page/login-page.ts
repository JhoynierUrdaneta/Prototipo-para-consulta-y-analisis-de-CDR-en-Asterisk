import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { AuthService } from '../../../shared/services/auth.service';
import { mensajeError } from '../../../shared/utils/errores';

@Component({
  selector: 'app-login-page',
  imports: [ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './login-page.html',
  styleUrl: './login-page.scss',
})
export class LoginPage {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly ruta = inject(ActivatedRoute);

  protected readonly enviando = signal(false);
  protected readonly error = signal('');

  protected readonly form = this.fb.nonNullable.group({
    correo: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]],
  });

  protected enviar(): void {
    if (this.form.invalid || this.enviando()) {
      this.form.markAllAsTouched();
      return;
    }
    this.enviando.set(true);
    this.error.set('');

    const { correo, password } = this.form.getRawValue();
    this.auth.login(correo, password).subscribe({
      next: () => {
        const destino = this.ruta.snapshot.queryParamMap.get('returnUrl') ?? '/app';
        void this.router.navigateByUrl(destino);
      },
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudo iniciar sesión'));
        this.enviando.set(false);
      },
    });
  }
}
