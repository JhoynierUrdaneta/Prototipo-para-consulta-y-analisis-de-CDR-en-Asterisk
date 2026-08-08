from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://callcenter:callcenter@db:5432/callcenter_ai"
    # Clave maestra para cifrar los secretos de integraciones (OpenAI/Supabase) en la BD.
    app_secret_key: str = "dev-app-secret-change-me"
    jwt_secret: str = "dev-jwt-secret-change-me"
    jwt_expire_min: int = 720
    cors_origins: str = "*"

    # Usuarios iniciales (solo se crean si la tabla usuarios está vacía).
    # Contraseñas fuertes y memorables; se pueden sobrescribir por variables de entorno.
    admin_email: str = "admin@estadiscall.com"
    admin_password: str = "Estadis.Admin.2026"
    supervisor_password: str = "Estadis.Super.2026"
    coordinador_password: str = "Estadis.Coord.2026"
    financiero_password: str = "Estadis.Finanzas.2026"

    env: str = "dev"  # "production" activa avisos de seguridad
    consulta_max_por_min: int = 20
    chat_retencion_dias: int = 30  # el historial de chat se elimina automáticamente pasado este plazo
    # Clave compartida entre backend y el contenedor cloudflared (endpoint interno del token)
    internal_key: str = "dev-internal-key"


settings = Settings()
