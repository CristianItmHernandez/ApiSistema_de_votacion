"""
Capa de infraestructura de base de datos.
Expone: engine, SessionLocal, Base y la dependencia get_db().
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# connect_args solo es necesario para SQLite (evita errores de threading)
_connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM (SQLAlchemy 2.0)."""

    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependencia FastAPI que provee una sesión de base de datos por request.
    Garantiza el cierre de la sesión en el bloque finally (constitution §5).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
