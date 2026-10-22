"""
Schemas Pydantic para Vote.
"""
from pydantic import BaseModel, ConfigDict


class VoteCreate(BaseModel):
    """DTO de entrada para emitir un voto."""

    voter_id: int
    candidate_id: int


class VoteResponse(BaseModel):
    """DTO de salida para representar un voto emitido."""

    id: int
    voter_id: int
    candidate_id: int

    model_config = ConfigDict(from_attributes=True)
