"""
Router de votos — capa de presentación (HTTP).
Incluye endpoints de emisión de votos, estadísticas y gráfica.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.statistics import VotingStatistics
from app.schemas.vote import VoteCreate, VoteResponse
from app.services import stats_service, vote_service

router = APIRouter(prefix="/votes", tags=["Votos"])


@router.post(
    "/",
    response_model=VoteResponse,
    status_code=201,
    summary="Emitir un voto",
)
def cast_vote(data: VoteCreate, db: Session = Depends(get_db)) -> VoteResponse:
    """
    Emite un voto de forma atómica.
    Verifica existencia de votante y candidato, y que el votante no haya votado ya.
    """
    return vote_service.cast_vote(db, data)


@router.get(
    "/",
    response_model=list[VoteResponse],
    status_code=200,
    summary="Listar todos los votos emitidos",
)
def list_votes(db: Session = Depends(get_db)) -> list[VoteResponse]:
    """Retorna el registro completo de votos emitidos."""
    return vote_service.get_votes(db)


@router.get(
    "/statistics",
    response_model=VotingStatistics,
    status_code=200,
    summary="Obtener estadísticas de votación",
)
def get_statistics(db: Session = Depends(get_db)) -> VotingStatistics:
    """
    Retorna totales y porcentajes de votos por candidato.
    Funciona correctamente incluso con 0 votos emitidos.
    """
    return stats_service.get_voting_statistics(db)


@router.get(
    "/statistics/chart",
    status_code=200,
    summary="Generar gráfica de resultados",
)
def get_chart(db: Session = Depends(get_db)) -> FileResponse:
    """
    Genera en tiempo real una gráfica de barras (Pandas + Matplotlib)
    con los votos actuales por candidato y la devuelve como imagen PNG.
    """
    chart_path = stats_service.generate_votes_chart(db)
    return FileResponse(chart_path, media_type="image/png")
