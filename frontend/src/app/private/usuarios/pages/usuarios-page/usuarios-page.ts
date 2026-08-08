import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';

import { Usuario } from '../../../../shared/models/usuario.model';
import { AuthService } from '../../../../shared/services/auth.service';
import { UsuariosService } from '../../../../shared/services/usuarios.service';
import { mensajeError } from '../../../../shared/utils/errores';
import { UsuarioFormModal } from '../../components/usuario-form-modal/usuario-form-modal';

@Component({
  selector: 'app-usuarios-page',
  imports: [UsuarioFormModal],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './usuarios-page.html',
  styleUrl: './usuarios-page.scss',
})
export class UsuariosPage {
  private readonly usuarios = inject(UsuariosService);
  private readonly auth = inject(AuthService);

  protected readonly lista = signal<Usuario[]>([]);
  protected readonly cargando = signal(true);
  protected readonly error = signal('');
  protected readonly modalAbierto = signal(false);
  protected readonly enEdicion = signal<Usuario | null>(null);

  protected readonly yo = this.auth.usuario;

  constructor() {
    this.cargar();
  }

  protected abrirNuevo(): void {
    this.enEdicion.set(null);
    this.modalAbierto.set(true);
  }

  protected abrirEdicion(u: Usuario): void {
    this.enEdicion.set(u);
    this.modalAbierto.set(true);
  }

  protected alGuardar(): void {
    this.modalAbierto.set(false);
    this.cargar();
  }

  protected desactivar(u: Usuario): void {
    if (!confirm(`¿Desactivar a "${u.nombre}"? Conservará su histórico pero no podrá entrar.`)) {
      return;
    }
    this.usuarios.desactivar(u.id).subscribe({
      next: () => this.cargar(),
      error: (err: unknown) => this.error.set(mensajeError(err)),
    });
  }

  protected reactivar(u: Usuario): void {
    this.usuarios.actualizar(u.id, { activo: true }).subscribe({
      next: () => this.cargar(),
      error: (err: unknown) => this.error.set(mensajeError(err)),
    });
  }

  private cargar(): void {
    this.cargando.set(true);
    this.usuarios.listar().subscribe({
      next: (us) => {
        this.lista.set(us);
        this.cargando.set(false);
      },
      error: (err: unknown) => {
        this.error.set(mensajeError(err, 'No se pudieron cargar los usuarios'));
        this.cargando.set(false);
      },
    });
  }
}
