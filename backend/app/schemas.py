from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field

Perfil = Literal["admin", "supervisor", "coordinador", "financiero"]


class LoginIn(BaseModel):
    correo: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    correo: str
    nombre: str
    perfil: Perfil
    activo: bool


class LoginOut(BaseModel):
    token: str
    usuario: UserOut


class UserCreate(BaseModel):
    correo: EmailStr
    nombre: str
    password: str
    perfil: Perfil


class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    perfil: Optional[Perfil] = None
    activo: Optional[bool] = None
    password: Optional[str] = None


# ---------- Integraciones ----------
class OpenAIConfig(BaseModel):
    api_key: Optional[str] = None  # opcional al actualizar: si viene vacío se conserva el existente
    model: str = "gpt-4o"
    base_url: Optional[str] = None


class SupabaseConfig(BaseModel):
    url: Optional[str] = None  # https://<ref>.supabase.co
    db_host: str
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str
    db_password: Optional[str] = None  # opcional al actualizar
    anon_key: Optional[str] = None


# ---------- Dashboards / widgets ----------
class WidgetSpec(BaseModel):
    titulo: str
    sql: str
    tipo_grafico: str = "table"
    eje_x: Optional[str] = None
    series: list[str] = []
    descripcion: Optional[str] = None
    insight: Optional[str] = None


class DashboardIn(BaseModel):
    nombre: str
    definicion: list[WidgetSpec] = []


class DashboardUpdate(BaseModel):
    nombre: Optional[str] = None
    definicion: Optional[list[WidgetSpec]] = None
    compartido: Optional[bool] = None


# ---------- Exportación ----------
class ExportExcelIn(BaseModel):
    titulo: str = "Informe"
    columnas: list[str]
    filas: list[dict]


class ExportPdfIn(BaseModel):
    titulo: str = "Informe"
    insight: Optional[str] = None
    recomendaciones: list[str] = []
    columnas: list[str]
    filas: list[dict]
    chart_png: Optional[str] = None  # dataURL (image/png;base64,...)


# ---------- Cloudflare ----------
class CloudflareConfig(BaseModel):
    tunnel_token: str


# ---------- SMTP ----------
class SMTPConfig(BaseModel):
    host: str
    port: int = 587
    user: str
    password: Optional[str] = None  # opcional al actualizar
    from_email: Optional[str] = None
    use_tls: bool = True


# ---------- Informes programados ----------
class InformeIn(BaseModel):
    nombre: str
    dashboard_id: str
    destinatarios: str  # correos separados por coma
    hora: str = Field(pattern=r"^\d{2}:\d{2}$")  # HH:MM (hora Colombia)
    frecuencia: str = "diario"  # diario | habiles


class InformeUpdate(BaseModel):
    nombre: Optional[str] = None
    destinatarios: Optional[str] = None
    hora: Optional[str] = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    frecuencia: Optional[str] = None
    activo: Optional[bool] = None
