"""
Servicio de votantes — capa de lógica de negocio.
Prohibido: consultas directas en routers. Solo este módulo accede a los modelos Voter/Candidate.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.voter import Voter
from app.schemas.voter import VoterCreate

from fastapi import HTTPException


def create_voter(db: Session, data: VoterCreate) -> Voter:
    """
    Registra un nuevo votante.
    Aplica validación cruzada (no puede ser candidato) y unicidad de email.
    """
    clean_name = data.name.strip().lower()

    # Validación cruzada: no puede ser candidato (constitution §3.1)
    existing_candidate = db.query(Candidate).filter(
        func.lower(func.trim(Candidate.name)) == clean_name
    ).first()
    if existing_candidate:
        raise HTTPException(
            status_code=400,
            detail="Un candidato registrado no puede ser inscrito como votante.",
        )

    # Unicidad de email
    existing_email = db.query(Voter).filter(Voter.email == data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="El correo electrónico ya está registrado.",
        )

    voter = Voter(name=data.name.strip(), email=data.email, has_voted=False)
    db.add(voter)
    db.commit()
    db.refresh(voter)
    return voter


def get_voters(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    has_voted: bool | None = None,
    search: str | None = None,
) -> list[Voter]:
    """Lista votantes con paginación y filtros opcionales."""
    query = db.query(Voter)

    if has_voted is not None:
        query = query.filter(Voter.has_voted == has_voted)

    if search:
        query = query.filter(Voter.name.ilike(f"%{search}%"))

    return query.offset(skip).limit(limit).all()


def delete_voter(db: Session, voter_id: int) -> dict:
    """
    Elimina un votante.
    Rechaza la eliminación si el votante ya emitió su voto (constitution §3.4).
    """
    voter = db.query(Voter).filter(Voter.id == voter_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="El votante especificado no existe.")

    if voter.has_voted:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar un votante que ya ha emitido su voto.",
        )

    db.delete(voter)
    db.commit()
    return {"detail": f"Votante con id {voter_id} eliminado correctamente."}
