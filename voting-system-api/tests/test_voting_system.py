"""
Suite de pruebas oficial — Fase 4.
8 casos obligatorios según spec §3.
"""
from fastapi.testclient import TestClient

from app.auth.security import auth_settings, oauth2_scheme
from app.main import app


# ── helpers ───────────────────────────────────────────────────────────────────

def _voter(client: TestClient, name: str, email: str) -> dict:
    r = client.post("/voters/", json={"name": name, "email": email})
    assert r.status_code == 201, r.text
    return r.json()


def _candidate(client: TestClient, name: str, party: str = "Partido Test") -> dict:
    r = client.post("/candidates/", json={"name": name, "party": party})
    assert r.status_code == 201, r.text
    return r.json()


def _vote(client: TestClient, voter_id: int, candidate_id: int) -> dict:
    r = client.post("/votes/", json={"voter_id": voter_id, "candidate_id": candidate_id})
    assert r.status_code == 201, r.text
    return r.json()


# ── caso 1 ────────────────────────────────────────────────────────────────────

def test_register_voter_success(client: TestClient):
    """Crea un votante y verifica que has_voted sea False."""
    body = _voter(client, "Laura Sanchez", "laura@test.com")
    assert body["has_voted"] is False


# ── caso 2 ────────────────────────────────────────────────────────────────────

def test_register_candidate_success(client: TestClient):
    """Crea un candidato y verifica que votes sea 0."""
    body = _candidate(client, "Pedro Alonso")
    assert body["votes"] == 0


# ── caso 3 ────────────────────────────────────────────────────────────────────

def test_voter_cannot_be_candidate(client: TestClient):
    """
    Crea votante 'Carlos Ruiz', intenta crear candidato 'carlos ruiz'.
    Debe retornar 400 Bad Request (validación cruzada, constitution §3.1).
    """
    _voter(client, "Carlos Ruiz", "carlos@test.com")
    r = client.post("/candidates/", json={"name": "carlos ruiz", "party": "X"})
    assert r.status_code == 400
    assert "votante" in r.json()["detail"].lower()


# ── caso 4 ────────────────────────────────────────────────────────────────────

def test_candidate_cannot_be_voter(client: TestClient):
    """
    Crea candidata 'Elena Diaz', intenta crear votante 'Elena Diaz'.
    Debe retornar 400 Bad Request (validación cruzada, constitution §3.1).
    """
    _candidate(client, "Elena Diaz")
    r = client.post("/voters/", json={"name": "Elena Diaz", "email": "elena@test.com"})
    assert r.status_code == 400
    assert "candidato" in r.json()["detail"].lower()


# ── caso 5 ────────────────────────────────────────────────────────────────────

def test_cast_vote_and_integrity(client: TestClient):
    """
    Emite un voto válido y verifica:
    - voter.has_voted == True
    - candidate.votes == 1
    (constitution §3.3 — transacción atómica)
    """
    voter = _voter(client, "Marco Polo", "marco@test.com")
    candidate = _candidate(client, "Julieta Verne")
    _vote(client, voter["id"], candidate["id"])

    # Verificar has_voted
    voters = client.get("/voters/").json()
    found = next(v for v in voters if v["id"] == voter["id"])
    assert found["has_voted"] is True

    # Verificar candidate.votes via estadísticas
    stats = client.get("/votes/statistics").json()
    result = next(c for c in stats["results_by_candidate"] if c["candidate_id"] == candidate["id"])
    assert result["votes"] == 1


# ── caso 6 ────────────────────────────────────────────────────────────────────

def test_prevent_double_voting(client: TestClient):
    """
    Emite un segundo voto con el mismo voter_id.
    Debe retornar 400 Bad Request (constitution §3.2 — unicidad de voto).
    """
    voter = _voter(client, "Ana Repite", "ana@test.com")
    candidate = _candidate(client, "Bernardo Unico")
    _vote(client, voter["id"], candidate["id"])

    r2 = client.post("/votes/", json={"voter_id": voter["id"], "candidate_id": candidate["id"]})
    assert r2.status_code == 400
    assert "ya ha emitido" in r2.json()["detail"].lower()


# ── caso 7 ────────────────────────────────────────────────────────────────────

def test_cannot_delete_voter_who_voted(client: TestClient):
    """
    DELETE /voters/{id} de un votante que ya votó.
    Debe retornar 409 Conflict (constitution §3.4 — protección del historial).
    """
    voter = _voter(client, "Borrar Votado", "borrar@test.com")
    candidate = _candidate(client, "Cand Borrar")
    _vote(client, voter["id"], candidate["id"])

    r = client.delete(f"/voters/{voter['id']}")
    assert r.status_code == 409


# ── caso 8 ────────────────────────────────────────────────────────────────────

def test_statistics_and_chart_generation(client: TestClient):
    """
    - GET /votes/statistics: verifica porcentaje exacto (constitution §3.5).
    - GET /votes/statistics/chart: verifica status 200 y content-type image/png.
    """
    voter = _voter(client, "Stat Voter", "stat@test.com")
    candidate = _candidate(client, "Stat Cand")
    _vote(client, voter["id"], candidate["id"])

    # Estadísticas con 1 voto emitido y 1 candidato → 100%
    stats = client.get("/votes/statistics").json()
    assert stats["total_voters_voted"] == 1
    result = next(c for c in stats["results_by_candidate"] if c["candidate_id"] == candidate["id"])
    assert result["votes"] == 1
    assert result["percentage"] == 100.0

    # Gráfica PNG
    chart = client.get("/votes/statistics/chart")
    assert chart.status_code == 200
    assert chart.headers["content-type"] == "image/png"


def test_auth_enabled_requires_bearer_token(client: TestClient, monkeypatch):
    """Al activar JWT, los routers de votantes, candidatos y votos exigen token."""
    monkeypatch.setattr(auth_settings, "AUTH_ENABLED", True)
    protected_paths = ("/voters/", "/candidates/", "/votes/statistics")

    for path in protected_paths:
        response = client.get(path)
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"

    token_response = client.post(
        "/auth/token",
        data={
            "username": auth_settings.ADMIN_USERNAME,
            "password": auth_settings.ADMIN_PASSWORD,
        },
    )
    assert token_response.status_code == 200, token_response.text
    headers = {"Authorization": f"Bearer {token_response.json()['access_token']}"}

    for path in protected_paths:
        response = client.get(path, headers=headers)
        assert response.status_code == 200, response.text


def test_swagger_security_follows_auth_enabled(monkeypatch):
    protected_paths = ("/voters/", "/candidates/", "/votes/statistics")

    monkeypatch.setattr(auth_settings, "AUTH_ENABLED", False)
    disabled_schema = app.openapi()
    for path in protected_paths:
        assert "security" not in disabled_schema["paths"][path]["get"]
    assert "securitySchemes" not in disabled_schema.get("components", {})

    monkeypatch.setattr(auth_settings, "AUTH_ENABLED", True)
    enabled_schema = app.openapi()
    for path in protected_paths:
        assert enabled_schema["paths"][path]["get"]["security"]
    assert oauth2_scheme.scheme_name in enabled_schema["components"]["securitySchemes"]
    assert "security" not in enabled_schema["paths"]["/auth/token"]["post"]
