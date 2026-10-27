"""
Router de votantes — capa de presentación (HTTP).
Solo define rutas, status codes e inyección de dependencias.
Toda la lógica de negocio delega a voter_service.

La dependencia get_current_admin se aplica a nivel de router:
- AUTH_ENABLED=False (default) → pasa sin token.
- AUTH_ENABLED=True            → exige Bearer token válido en cada request.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.security import get_current_admin
from app.database import get_db
from app.schemas.voter import VoterCreate, VoterResponse
from app.services import voter_service

router = APIRouter(
    prefix="/voters",
    tags=["Votantes"],
    dependencies=[Depends(get_current_admin)],
)


@router.post(
    "/",
    response_model=VoterResponse,
    status_code=201,
    summary="Registrar un nuevo votante",
)
def register_voter(data: VoterCreate, db: Session = Depends(get_db)) -> VoterResponse:
    """Registra un votante verificando que no sea candidato y que el email sea único."""
    return voter_service.create_voter(db, data)


@router.get(
    "/",
    response_model=list[VoterResponse],
    status_code=200,
    summary="Listar votantes",
)
def list_voters(
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Máximo de registros a retornar"),
    has_voted: bool | None = Query(None, description="Filtrar por estado de voto"),
    search: str | None = Query(None, description="Búsqueda parcial por nombre"),
    db: Session = Depends(get_db),
) -> list[VoterResponse]:
    """Lista votantes con paginación y filtros opcionales."""
    return voter_service.get_voters(db, skip=skip, limit=limit, has_voted=has_voted, search=search)


@router.delete(
    "/{voter_id}",
    status_code=200,
    summary="Eliminar un votante",
)
def remove_voter(voter_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Elimina un votante por id.
    Retorna 409 si el votante ya emitió su voto (protección del historial electoral).
    """
    return voter_service.delete_voter(db, voter_id)
