import { ChangeDetectionStrategy, Component, inject, input, output, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { PERFILES, Perfil, Usuario } from '../../../../shared/models/usuario.model';
import { UsuariosService } from '../../../../shared/services/usuarios.service';
import { mensajeError } from '../../../../shared/utils/errores';

@Component({
  selector: 'app-usuario-form-modal',
  imports: [ReactiveFormsModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './usuario-form-modal.html',
})
export class UsuarioFormModal {
  private readonly fb = inject(FormBuilder);
  private readonly usuarios = inject(UsuariosService);

  readonly usuario = input<Usuario | null>(null);
  readonly cerrar = output<void>();
  readonly guardado = output<void>();

  protected readonly perfiles = PERFILES;
  protected readonly enviando = signal(false);
  protected readonly error = signal('');

  protected readonly form = this.fb.nonNullable.group({
    correo: ['', [Validators.required, Validators.email]],
    nombre: ['', Validators.required],
    password: ['', [Validators.required, Validators.minLength(8)]],
    perfil: ['supervisor' as Perfil, Validators.required],
  });

  constructor() {
    const actual = this.usuario();
    if (actual) {
      this.form.patchValue({
        correo: actual.correo,
        nombre: actual.nombre,
        perfil: actual.perfil,
      });
      // El correo es la identidad de la cuenta: el backend no lo actualiza.
      this.form.controls.correo.disable();
      // Al editar, la contraseña es opcional: vacía = se conserva la actual.
      this.form.controls.password.setValidators([Validators.minLength(8)]);
      this.form.controls.password.updateValueAndValidity();
    }
  }

  protected enviar(): void {
    if (this.form.invalid || this.enviando()) {
      this.form.markAllAsTouched();
      return;
    }
    this.enviando.set(true);
    this.error.set('');

    const v = this.form.getRawValue();
    const actual = this.usuario();

    const peticion = actual
      ? this.usuarios.actualizar(actual.id, {
          nombre: v.nombre,
          perfil: v.perfil,
          ...(v.password ? { password: v.password } : {}),
        })
      : this.usuarios.crear(v);

    peticion.subscribe({
      next: () => this.guardado.emit(),
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudo guardar el usuario'));
        this.enviando.set(false);
      },
    });
  }
}
