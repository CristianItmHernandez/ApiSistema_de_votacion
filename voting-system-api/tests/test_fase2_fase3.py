"""
Tests de integración: DoD Fase 2 + Fase 3.
Usa SQLite en memoria para no contaminar la BD de desarrollo.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.candidate import Candidate
from app.models.vote import Vote
from app.models.voter import Voter

# --- Configuración de BD en memoria para tests ---
TEST_DATABASE_URL = "sqlite:///./test_voting.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Crear tablas UNA SOLA VEZ al cargar el módulo
Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_tables():
    """Limpia los datos entre cada test manteniendo el schema."""
    yield
    with test_engine.connect() as conn:
        conn.execute(text("DELETE FROM votes"))
        conn.execute(text("DELETE FROM voters"))
        conn.execute(text("DELETE FROM candidates"))
        conn.commit()


# ─────────────────────────────────────────────
# DoD FASE 2
# ─────────────────────────────────────────────

def test_create_voter_success():
    """POST /voters debe retornar 201 con datos correctos."""
    r = client.post("/voters/", json={"name": "Ana Lopez", "email": "ana@test.com"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Ana Lopez"
    assert body["has_voted"] is False


def test_create_candidate_success():
    """POST /candidates debe retornar 201."""
    r = client.post("/candidates/", json={"name": "Carlos Ruiz", "party": "Partido A"})
    assert r.status_code == 201
    assert r.json()["votes"] == 0


def test_cross_validation_voter_cannot_be_candidate():
    """DoD Fase 2: votante registrado no puede ser inscrito como candidato (400)."""
    client.post("/voters/", json={"name": "Juan Perez", "email": "juan@test.com"})
    # Variante con espacios y distinta capitalización
    r = client.post("/candidates/", json={"name": "juan perez ", "party": "X"})
    assert r.status_code == 400
    assert "votante" in r.json()["detail"].lower()


def test_cross_validation_candidate_cannot_be_voter():
    """DoD Fase 2: candidata registrada no puede ser inscrita como votante (400)."""
    client.post("/candidates/", json={"name": "Maria Gomez", "party": "Y"})
    r = client.post("/voters/", json={"name": "Maria Gomez", "email": "maria@test.com"})
    assert r.status_code == 400
    assert "candidato" in r.json()["detail"].lower()


def test_duplicate_email_returns_409():
    """Email duplicado en voters debe retornar 409."""
    client.post("/voters/", json={"name": "Pedro", "email": "dup@test.com"})
    r = client.post("/voters/", json={"name": "Pedro2", "email": "dup@test.com"})
    assert r.status_code == 409


def test_duplicate_candidate_returns_409():
    """Candidato con nombre duplicado debe retornar 409."""
    client.post("/candidates/", json={"name": "Sofia", "party": "Z"})
    r = client.post("/candidates/", json={"name": "Sofia", "party": "Z"})
    assert r.status_code == 409


def test_list_voters_pagination():
    """DoD Fase 2: skip y limit funcionan correctamente."""
    for i in range(5):
        client.post("/voters/", json={"name": f"Voter {i}", "email": f"v{i}@test.com"})
    r = client.get("/voters/?skip=2&limit=2")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_delete_voter_not_voted():
    """DELETE /voters/{id} elimina correctamente si el votante no ha votado."""
    r = client.post("/voters/", json={"name": "Temporal", "email": "tmp@test.com"})
    vid = r.json()["id"]
    r2 = client.delete(f"/voters/{vid}")
    assert r2.status_code == 200


def test_delete_voter_already_voted_returns_409():
    """DoD Fase 2/Constitution §3.4: no se puede eliminar votante que ya votó (409)."""
    rv = client.post("/voters/", json={"name": "Votador", "email": "vd@test.com"})
    rc = client.post("/candidates/", json={"name": "Candidato Final", "party": "P"})
    vid = rv.json()["id"]
    cid = rc.json()["id"]
    client.post("/votes/", json={"voter_id": vid, "candidate_id": cid})
    r = client.delete(f"/voters/{vid}")
    assert r.status_code == 409


# ─────────────────────────────────────────────
# DoD FASE 3
# ─────────────────────────────────────────────

def test_cast_vote_success():
    """DoD Fase 3: voto exitoso → has_voted=True, candidate.votes sube en 1."""
    rv = client.post("/voters/", json={"name": "Elector", "email": "el@test.com"})
    rc = client.post("/candidates/", json={"name": "Candidato Test", "party": "PT"})
    vid = rv.json()["id"]
    cid = rc.json()["id"]

    r = client.post("/votes/", json={"voter_id": vid, "candidate_id": cid})
    assert r.status_code == 201

    # Verificar has_voted
    voters_r = client.get("/voters/")
    voter = next(v for v in voters_r.json() if v["id"] == vid)
    assert voter["has_voted"] is True

    # Verificar candidate.votes via estadísticas
    stats = client.get("/votes/statistics").json()
    result = next(c for c in stats["results_by_candidate"] if c["candidate_id"] == cid)
    assert result["votes"] == 1


def test_double_vote_returns_400():
    """DoD Fase 3: segundo voto del mismo votante retorna 400 y no altera conteo."""
    rv = client.post("/voters/", json={"name": "Doble", "email": "doble@test.com"})
    rc = client.post("/candidates/", json={"name": "Cand Doble", "party": "D"})
    vid = rv.json()["id"]
    cid = rc.json()["id"]

    client.post("/votes/", json={"voter_id": vid, "candidate_id": cid})
    r2 = client.post("/votes/", json={"voter_id": vid, "candidate_id": cid})
    assert r2.status_code == 400

    # Conteo no se alteró
    stats = client.get("/votes/statistics").json()
    result = next(c for c in stats["results_by_candidate"] if c["candidate_id"] == cid)
    assert result["votes"] == 1


def test_statistics_zero_votes_no_division_error():
    """DoD Fase 3: estadísticas con 0 votos retornan 200 y percentage=0.0."""
    client.post("/candidates/", json={"name": "Sin Votos", "party": "SV"})
    r = client.get("/votes/statistics")
    assert r.status_code == 200
    body = r.json()
    assert body["total_voters_voted"] == 0
    for c in body["results_by_candidate"]:
        assert c["percentage"] == 0.0


def test_chart_generation():
    """DoD Fase 3: GET /votes/statistics/chart retorna 200 con content-type image/png."""
    client.post("/candidates/", json={"name": "Cand Chart", "party": "CH"})
    r = client.get("/votes/statistics/chart")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
