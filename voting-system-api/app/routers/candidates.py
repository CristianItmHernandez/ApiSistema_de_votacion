"""
Router de candidatos — capa de presentación (HTTP).
Solo define rutas, status codes e inyección de dependencias.
Toda la lógica de negocio delega a candidate_service.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.candidate import CandidateCreate, CandidateResponse
from app.services import candidate_service

router = APIRouter(prefix="/candidates", tags=["Candidatos"])


@router.post(
    "/",
    response_model=CandidateResponse,
    status_code=201,
    summary="Registrar un nuevo candidato",
)
def register_candidate(data: CandidateCreate, db: Session = Depends(get_db)) -> CandidateResponse:
    """Registra un candidato verificando que no sea votante y que el nombre sea único."""
    return candidate_service.create_candidate(db, data)


@router.get(
    "/",
    response_model=list[CandidateResponse],
    status_code=200,
    summary="Listar candidatos",
)
def list_candidates(
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Máximo de registros a retornar"),
    party: str | None = Query(None, description="Filtrar por partido político"),
    db: Session = Depends(get_db),
) -> list[CandidateResponse]:
    """Lista candidatos con paginación y filtro opcional por partido."""
    return candidate_service.get_candidates(db, skip=skip, limit=limit, party=party)
