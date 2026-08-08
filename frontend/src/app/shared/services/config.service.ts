import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  CloudflareEstado,
  OpenAIEstado,
  OpenAIGuardar,
  PruebaOpenAI,
  PruebaSupabase,
  SmtpEstado,
  SmtpGuardar,
  SupabaseEstado,
  SupabaseGuardar,
} from '../models/config.model';

/**
 * backend/app/routers/config.py — integraciones cifradas (solo admin).
 * En todos los PUT/test, si el secreto va vacío el backend reutiliza el que
 * ya tiene guardado, así que nunca hace falta reescribirlo para editar el resto.
 */
@Injectable({ providedIn: 'root' })
export class ConfigService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/config`;

  // ── OpenAI ──
  obtenerOpenai(): Observable<OpenAIEstado> {
    return this.http.get<OpenAIEstado>(`${this.base}/openai`);
  }

  guardarOpenai(body: OpenAIGuardar): Observable<{ ok: boolean }> {
    return this.http.put<{ ok: boolean }>(`${this.base}/openai`, body);
  }

  probarOpenai(body: OpenAIGuardar): Observable<PruebaOpenAI> {
    return this.http.post<PruebaOpenAI>(`${this.base}/openai/test`, body);
  }

  // ── Supabase ──
  obtenerSupabase(): Observable<SupabaseEstado> {
    return this.http.get<SupabaseEstado>(`${this.base}/supabase`);
  }

  guardarSupabase(body: SupabaseGuardar): Observable<{ ok: boolean }> {
    return this.http.put<{ ok: boolean }>(`${this.base}/supabase`, body);
  }

  probarSupabase(body: SupabaseGuardar): Observable<PruebaSupabase> {
    return this.http.post<PruebaSupabase>(`${this.base}/supabase/test`, body);
  }

  // ── SMTP ──
  obtenerSmtp(): Observable<SmtpEstado> {
    return this.http.get<SmtpEstado>(`${this.base}/smtp`);
  }

  guardarSmtp(body: SmtpGuardar): Observable<{ ok: boolean }> {
    return this.http.put<{ ok: boolean }>(`${this.base}/smtp`, body);
  }

  probarSmtp(body: SmtpGuardar): Observable<{ ok: boolean }> {
    return this.http.post<{ ok: boolean }>(`${this.base}/smtp/test`, body);
  }

  // ── Cloudflare ──
  obtenerCloudflare(): Observable<CloudflareEstado> {
    return this.http.get<CloudflareEstado>(`${this.base}/cloudflare`);
  }

  guardarCloudflare(tunnelToken: string): Observable<{ ok: boolean }> {
    return this.http.put<{ ok: boolean }>(`${this.base}/cloudflare`, {
      tunnel_token: tunnelToken,
    });
  }

  eliminarCloudflare(): Observable<void> {
    return this.http.delete<void>(`${this.base}/cloudflare`);
  }
}
