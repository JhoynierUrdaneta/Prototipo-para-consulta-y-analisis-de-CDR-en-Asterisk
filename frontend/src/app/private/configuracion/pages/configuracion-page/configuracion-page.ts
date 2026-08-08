import { ChangeDetectionStrategy, Component } from '@angular/core';

import { CloudflareCard } from '../../components/cloudflare-card/cloudflare-card';
import { OpenaiCard } from '../../components/openai-card/openai-card';
import { SmtpCard } from '../../components/smtp-card/smtp-card';
import { SupabaseCard } from '../../components/supabase-card/supabase-card';

@Component({
  selector: 'app-configuracion-page',
  imports: [OpenaiCard, SupabaseCard, SmtpCard, CloudflareCard],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './configuracion-page.html',
  styleUrl: './configuracion-page.scss',
})
export class ConfiguracionPage {}
