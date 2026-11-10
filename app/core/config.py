import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./cafeteria.db"

    # Si no se define SECRET_KEY en el .env se genera una al iniciar (los tokens dejan de servir al reiniciar)
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    algoritmo_jwt: str = "HS256"
    minutos_expiracion_token: int = 60

    admin_usuario: str = "admin"
    admin_password: str = "Admin123*"
    cajero_usuario: str = "cajero"
    cajero_password: str = "Cajero123*"
    cargar_datos_demo: bool = True


settings = Settings()
