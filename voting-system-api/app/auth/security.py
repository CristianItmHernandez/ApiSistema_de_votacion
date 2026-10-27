"""
Módulo de seguridad JWT.

Estrategia según spec §2:
- AUTH_ENABLED = False  →  endpoints no requieren token (modo evaluación/demo).
- AUTH_ENABLED = True   →  todos los endpoints protegidos exigen Bearer token.
- POST /auth/token siempre disponible para obtener el JWT.
- Swagger UI muestra el botón Authorize con OAuth2PasswordBearer.
"""
import datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from pydantic_settings import BaseSettings


# ── Configuración ─────────────────────────────────────────────────────────────

class AuthSettings(BaseSettings):
    """Variables de entorno para autenticación."""

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    JWT_SECRET_KEY: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    AUTH_ENABLED: bool = True

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


auth_settings = AuthSettings()

# OAuth2PasswordBearer expone el botón Authorize en /docs (spec DoD §4)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


# ── Schemas ───────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """Respuesta del endpoint /auth/token."""

    access_token: str
    token_type: str = "bearer"


# ── Lógica JWT ────────────────────────────────────────────────────────────────

def _create_access_token(subject: str) -> str:
    """Genera un JWT firmado con HS256."""
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=auth_settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(
        payload, auth_settings.JWT_SECRET_KEY, algorithm=auth_settings.JWT_ALGORITHM
    )


def login_for_token(form_data: OAuth2PasswordRequestForm) -> TokenResponse:
    """
    Valida credenciales de administrador y emite un JWT.
    Credenciales configurables vía variables de entorno ADMIN_USERNAME / ADMIN_PASSWORD.
    """
    if (
        form_data.username != auth_settings.ADMIN_USERNAME
        or form_data.password != auth_settings.ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de administrador incorrectas.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = _create_access_token(subject=form_data.username)
    return TokenResponse(access_token=token)


# ── Dependencia de seguridad ──────────────────────────────────────────────────

def get_current_admin(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> str | None:
    """
    Dependencia inyectable para proteger endpoints.

    - Si AUTH_ENABLED=False: acepta cualquier request (sin token).
    - Si AUTH_ENABLED=True: valida el Bearer token; rechaza con 401 si es inválido/ausente.
    """
    if not auth_settings.AUTH_ENABLED:
        return None  # Modo evaluación: seguridad desactivada

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación requerido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            token,
            auth_settings.JWT_SECRET_KEY,
            algorithms=[auth_settings.JWT_ALGORITHM],
        )
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
