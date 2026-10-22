"""
Configuración centralizada de la aplicación.
Lee variables de entorno desde el archivo .env (si existe),
con valores por defecto seguros para desarrollo local.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación leída desde variables de entorno."""

    DATABASE_URL: str = "sqlite:///./voting_system.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Retorna la instancia singleton de Settings (cacheada)."""
    return Settings()
