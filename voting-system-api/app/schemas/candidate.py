"""
Schemas Pydantic para Candidate.
"""
from pydantic import BaseModel, ConfigDict, Field


class CandidateCreate(BaseModel):
    """DTO de entrada para crear un candidato."""

    name: str = Field(min_length=2)
    party: str | None = None

    model_config = ConfigDict(str_strip_whitespace=True)


class CandidateResponse(BaseModel):
    """DTO de salida para representar un candidato."""

    id: int
    name: str
    party: str | None
    votes: int

    model_config = ConfigDict(from_attributes=True)
