// Espejo de backend/app/schemas.py (Perfil, UserOut, LoginIn/Out, UserCreate/Update).
export type Perfil = 'admin' | 'supervisor' | 'coordinador' | 'financiero';

export const PERFILES: Perfil[] = ['admin', 'supervisor', 'coordinador', 'financiero'];

export interface Usuario {
  id: string;
  correo: string;
  nombre: string;
  perfil: Perfil;
  activo: boolean;
}

export interface LoginIn {
  correo: string;
  password: string;
}

export interface LoginOut {
  token: string;
  usuario: Usuario;
}

export interface UsuarioCrear {
  correo: string;
  nombre: string;
  password: string;
  perfil: Perfil;
}

export interface UsuarioActualizar {
  nombre?: string;
  perfil?: Perfil;
  activo?: boolean;
  password?: string;
}
