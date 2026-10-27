"""
Punto de entrada de la aplicación FastAPI.
Registra los routers y crea las tablas al iniciar.
"""
from typing import Any

import app.models  # Necesario para que SQLAlchemy registre todos los modelos
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi

from app.auth.security import auth_settings, oauth2_scheme
from app.database import Base, engine
from app.routers import auth, candidates, voters, votes

# Crear tablas automáticamente al iniciar (constitution §1, criterio DoD Fase 1)
Base.metadata.create_all(bind=engine)

auth_description = (
    "JWT obligatorio en los endpoints protegidos."
    if auth_settings.AUTH_ENABLED
    else "JWT desactivado; los endpoints funcionan sin token."
)

app = FastAPI(
    title="Sistema de Votaciones API",
    description=(
        "API REST para gestión de votantes, candidatos y emisión de votos.\n\n"
        "## Autenticación\n"
        f"{auth_description}\n"
        "Cuando JWT está activo, obtené el token en `POST /auth/token` "
        "y usa **Authorize** para ingresarlo."
    ),
    version="1.0.0",
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "192.168.1.X"],
)

app.include_router(auth.router)
app.include_router(voters.router)
app.include_router(candidates.router)
app.include_router(votes.router)

_openapi_auth_enabled: bool | None = None


def custom_openapi() -> dict[str, Any]:
    global _openapi_auth_enabled

    if (
        app.openapi_schema is None
        or _openapi_auth_enabled != auth_settings.AUTH_ENABLED
    ):
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        if not auth_settings.AUTH_ENABLED:
            for path_item in schema.get("paths", {}).values():
                for operation in path_item.values():
                    if isinstance(operation, dict):
                        operation.pop("security", None)

            security_schemes = schema.get("components", {}).get("securitySchemes", {})
            security_schemes.pop(oauth2_scheme.scheme_name, None)
            if not security_schemes:
                schema.get("components", {}).pop("securitySchemes", None)
            if not schema.get("components"):
                schema.pop("components", None)

        app.openapi_schema = schema
        _openapi_auth_enabled = auth_settings.AUTH_ENABLED

    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", tags=["Root"])
def root() -> dict:
    """Health check del servicio."""
    return {"status": "ok", "message": "Sistema de Votaciones API funcionando correctamente."}
