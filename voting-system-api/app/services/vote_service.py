"""
Servicio de emisión de votos — transacción atómica ACID (constitution §3.3).
"""
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.vote import Vote
from app.models.voter import Voter
from app.schemas.vote import VoteCreate, VoteResponse

from fastapi import HTTPException


def cast_vote(db: Session, vote_data: VoteCreate) -> Vote:
    """
    Emite un voto de forma atómica.
    Pasos dentro de una única transacción:
      1. Insertar Vote
      2. Marcar voter.has_voted = True
      3. Incrementar candidate.votes += 1
    Ante cualquier excepción se ejecuta rollback.
    """
    # 1. Verificar existencia del votante
    voter = db.query(Voter).filter(Voter.id == vote_data.voter_id).first()
    if not voter:
        raise HTTPException(status_code=404, detail="El votante especificado no existe.")

    # 2. Verificar que no haya votado ya (constitution §3.2)
    if voter.has_voted:
        raise HTTPException(
            status_code=400,
            detail="El votante ya ha emitido un voto previamente.",
        )

    # 3. Verificar existencia del candidato
    candidate = db.query(Candidate).filter(Candidate.id == vote_data.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="El candidato especificado no existe.")

    # 4. Transacción atómica
    try:
        new_vote = Vote(voter_id=voter.id, candidate_id=candidate.id)
        voter.has_voted = True
        candidate.votes += 1
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        return new_vote
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error interno al registrar el voto. La operación fue revertida.",
        )


def get_votes(db: Session) -> list[Vote]:
    """Retorna todos los votos emitidos."""
    return db.query(Vote).all()
