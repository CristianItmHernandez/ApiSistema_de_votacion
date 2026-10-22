"""
Modelo ORM: Vote (tabla votes).
La restricción UNIQUE en voter_id garantiza a nivel de BD
que un votante solo puede emitir un voto (constitution §3.2).
"""
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Vote(Base):
    """Representa un voto emitido en el sistema."""

    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    voter_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("voters.id"),
        nullable=False,
        unique=True,  # 1 votante = 1 voto garantizado a nivel de BD
    )
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("candidates.id"), nullable=False
    )
