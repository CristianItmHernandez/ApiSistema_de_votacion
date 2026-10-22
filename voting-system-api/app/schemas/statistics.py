"""
Schemas Pydantic para estadísticas de votación.
"""
from pydantic import BaseModel


class CandidateResult(BaseModel):
    """Resultado de un candidato con porcentaje de votos."""

    candidate_id: int
    name: str
    party: str | None
    votes: int
    percentage: float


class VotingStatistics(BaseModel):
    """Estadísticas globales de la elección."""

    total_voters_voted: int
    results_by_candidate: list[CandidateResult]
