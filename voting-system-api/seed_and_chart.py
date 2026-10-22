"""
Script de demostración rápida (spec Fase 5 §2).

Uso:
    python seed_and_chart.py

Acciones:
  1. Crea 3 candidatos y 10 votantes en la BD.
  2. Simula 8 votos distribuidos entre candidatos.
  3. Imprime resumen de estadísticas en consola.
  4. Genera static/charts/voting_results.png con Pandas + Matplotlib.
"""
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Asegura que el directorio raíz esté en el path
sys.path.insert(0, ".")

import app.models  # noqa: E402 — necesario para registrar modelos en Base
from app.database import Base
from app.models.candidate import Candidate
from app.models.voter import Voter
from app.models.vote import Vote
from app.services import stats_service

# ── Configuración de BD ───────────────────────────────────────────────────────
DATABASE_URL = "sqlite:///./voting_system.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# ── Datos de ejemplo ──────────────────────────────────────────────────────────
CANDIDATES = [
    {"name": "Alejandra Vidal",   "party": "Partido Progresista"},
    {"name": "Ramón Delgado",     "party": "Frente Popular"},
    {"name": "Valentina Cruz",    "party": "Alianza Democrática"},
]

VOTERS = [
    {"name": f"Votante {i+1}", "email": f"votante{i+1}@demo.com"}
    for i in range(10)
]

# 8 votos: 4 → candidato 0, 3 → candidato 1, 1 → candidato 2
VOTE_DISTRIBUTION = [0, 0, 0, 0, 1, 1, 1, 2]


def seed():
    db = SessionLocal()
    try:
        # Limpiar datos anteriores del seed para permitir re-ejecución
        db.query(Vote).delete()
        db.query(Voter).delete()
        db.query(Candidate).delete()
        db.commit()

        # Crear candidatos
        candidates = []
        for c_data in CANDIDATES:
            c = Candidate(**c_data, votes=0)
            db.add(c)
            candidates.append(c)
        db.commit()
        for c in candidates:
            db.refresh(c)
        print(f"[OK] {len(candidates)} candidatos creados.")

        # Crear votantes
        voters = []
        for v_data in VOTERS:
            v = Voter(**v_data, has_voted=False)
            db.add(v)
            voters.append(v)
        db.commit()
        for v in voters:
            db.refresh(v)
        print(f"[OK] {len(voters)} votantes creados.")

        # Emitir votos
        for i, cand_idx in enumerate(VOTE_DISTRIBUTION):
            voter = voters[i]
            candidate = candidates[cand_idx]
            vote = Vote(voter_id=voter.id, candidate_id=candidate.id)
            voter.has_voted = True
            candidate.votes += 1
            db.add(vote)
        db.commit()
        print(f"[OK] {len(VOTE_DISTRIBUTION)} votos emitidos.\n")

        # Estadísticas
        stats = stats_service.get_voting_statistics(db)
        print("-" * 50)
        print(f"  Total votantes que votaron : {stats.total_voters_voted}")
        print("-" * 50)
        for r in stats.results_by_candidate:
            bar = "#" * r.votes
            print(f"  {r.name:<22} {r.votes:>2} votos  {r.percentage:>6.2f}%  {bar}")
        print("-" * 50)

        # Gráfica con Pandas
        chart_path = stats_service.generate_votes_chart(db)
        print(f"\n[OK] Grafica generada en: {chart_path}")
        print("     Abrila para ver la distribucion de votos.\n")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
