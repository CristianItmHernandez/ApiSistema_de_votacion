"""
Router de autenticación.
Expone POST /auth/token para obtener un JWT de administrador.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.security import TokenResponse, login_for_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Obtener token JWT de administrador",
    description=(
        "Recibe credenciales (`username` / `password`) y devuelve un Bearer token JWT. "
        "Por defecto: `admin` / `admin123`. "
        "Configurable vía variables de entorno `ADMIN_USERNAME` y `ADMIN_PASSWORD`."
    ),
)
def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    """Genera un JWT firmado con HS256 si las credenciales son correctas."""
    return login_for_token(form_data)
