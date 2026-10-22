"""
Schemas Pydantic para Voter.
"""
from pydantic import BaseModel, ConfigDict, EmailStr


class VoterCreate(BaseModel):
    """DTO de entrada para crear un votante."""

    name: str
    email: EmailStr

    model_config = ConfigDict(
        str_strip_whitespace=True,  # previene nombres de solo espacios
        str_min_length=2,           # aplica a todos los campos str (name)
    )


class VoterResponse(BaseModel):
    """DTO de salida para representar un votante."""

    id: int
    name: str
    email: str
    has_voted: bool

    model_config = ConfigDict(from_attributes=True)
