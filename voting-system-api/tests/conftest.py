"""
Fixtures compartidos para la suite de pruebas oficial (Fase 4).
BD SQLite en memoria — aislada y ultrarrápida (spec §3).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.auth.security import auth_settings
from app.database import Base, get_db
from app.main import app
from app.models.candidate import Candidate
from app.models.vote import Vote
from app.models.voter import Voter

TEST_DB_URL = "sqlite:///./test_official.db"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Schema creado una sola vez al cargar el módulo
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client() -> TestClient:
    """Cliente HTTP con BD de test inyectada."""
    return TestClient(app, base_url="http://localhost")


@pytest.fixture(autouse=True)
def auth_disabled_by_default(monkeypatch):
    """Mantiene las pruebas funcionales independientes del AUTH_ENABLED del entorno."""
    monkeypatch.setattr(auth_settings, "AUTH_ENABLED", False)


@pytest.fixture(autouse=True)
def clean_db():
    """Limpia todas las tablas entre cada test."""
    yield
    with test_engine.connect() as conn:
        conn.execute(text("DELETE FROM votes"))
        conn.execute(text("DELETE FROM voters"))
        conn.execute(text("DELETE FROM candidates"))
        conn.commit()
