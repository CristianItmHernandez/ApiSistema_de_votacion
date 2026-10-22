"""
Servicio de candidatos — capa de lógica de negocio.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.voter import Voter
from app.schemas.candidate import CandidateCreate

from fastapi import HTTPException


def create_candidate(db: Session, data: CandidateCreate) -> Candidate:
    """
    Registra un nuevo candidato.
    Aplica validación cruzada (no puede ser votante) y unicidad de nombre.
    """
    clean_name = data.name.strip().lower()

    # Validación cruzada: no puede ser votante (constitution §3.1)
    existing_voter = db.query(Voter).filter(
        func.lower(func.trim(Voter.name)) == clean_name
    ).first()
    if existing_voter:
        raise HTTPException(
            status_code=400,
            detail="Un votante registrado no puede ser inscrito como candidato.",
        )

    # Unicidad de nombre de candidato
    existing_candidate = db.query(Candidate).filter(
        func.lower(func.trim(Candidate.name)) == clean_name
    ).first()
    if existing_candidate:
        raise HTTPException(
            status_code=409,
            detail="El candidato ya se encuentra registrado.",
        )

    candidate = Candidate(
        name=data.name.strip(),
        party=data.party,
        votes=0,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def get_candidates(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    party: str | None = None,
) -> list[Candidate]:
    """Lista candidatos con paginación y filtro opcional por partido."""
    query = db.query(Candidate)

    if party:
        query = query.filter(Candidate.party.ilike(f"%{party}%"))

    return query.offset(skip).limit(limit).all()
