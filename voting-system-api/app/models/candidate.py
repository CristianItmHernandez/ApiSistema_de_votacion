"""
Modelo ORM: Candidate (tabla candidates).
"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Candidate(Base):
    """Representa un candidato en el sistema de votaciones."""

    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True, index=True
    )
    party: Mapped[str | None] = mapped_column(String(100), nullable=True)
    votes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
