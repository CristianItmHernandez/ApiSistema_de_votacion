"""
Modelo ORM: Voter (tabla voters).
"""
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Voter(Base):
    """Representa un votante registrado en el sistema."""

    __tablename__ = "voters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True, index=True
    )
    has_voted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
