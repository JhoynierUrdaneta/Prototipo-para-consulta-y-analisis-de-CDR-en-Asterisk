// Integraciones. Los GET devuelven los secretos enmascarados (_mask en
// backend/app/routers/config.py); los PUT aceptan el secreto opcional:
// si va vacío, el backend conserva el que ya tenía cifrado.

export interface OpenAIEstado {
  configurado: boolean;
  model: string;
  base_url?: string | null;
  api_key_mask?: string;
  updated_at?: string;
}

export interface OpenAIGuardar {
  api_key?: string;
  model: string;
  base_url?: string;
}

export interface SupabaseEstado {
  configurado: boolean;
  url?: string | null;
  db_host?: string;
  db_port: number;
  db_name: string;
  db_user?: string;
  db_password_mask?: string;
  anon_key_mask?: string;
  updated_at?: string;
}

export interface SupabaseGuardar {
  url?: string;
  db_host: string;
  db_port: number;
  db_name: string;
  db_user: string;
  db_password?: string;
  anon_key?: string;
}

export interface SmtpEstado {
  configurado: boolean;
  host?: string;
  port: number;
  user?: string;
  from_email?: string;
  use_tls: boolean;
  password_mask?: string;
  updated_at?: string;
}

export interface SmtpGuardar {
  host: string;
  port: number;
  user: string;
  password?: string;
  from_email?: string;
  use_tls: boolean;
}

export interface CloudflareEstado {
  configurado: boolean;
  token_mask?: string;
  updated_at?: string;
}

export interface PruebaOpenAI {
  ok: boolean;
  modelos_disponibles: number;
}

export interface PruebaSupabase {
  ok: boolean;
  server_version: string;
  tablas_public: number;
}
