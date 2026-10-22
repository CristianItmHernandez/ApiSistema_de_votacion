"""
Servicio de estadísticas y gráficas.
Usa Pandas + Matplotlib (backend Agg, no interactivo) para generar el chart.
"""
import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.voter import Voter
from app.schemas.statistics import CandidateResult, VotingStatistics

# Backend no interactivo obligatorio (constitution §1)
matplotlib.use("Agg")

CHART_DIR = os.path.join("static", "charts")
CHART_PATH = os.path.join(CHART_DIR, "voting_results.png")


def get_voting_statistics(db: Session) -> VotingStatistics:
    """
    Calcula las estadísticas de votación.
    Previene división por cero cuando total_voters_voted == 0 (constitution §3.5).
    """
    candidates = db.query(Candidate).all()
    total_voters_voted: int = (
        db.query(Voter).filter(Voter.has_voted == True).count()  # noqa: E712
    )

    results: list[CandidateResult] = []
    for candidate in candidates:
        if total_voters_voted > 0:
            percentage = round((candidate.votes / total_voters_voted) * 100, 2)
        else:
            percentage = 0.0  # Seguridad matemática: evita ZeroDivisionError

        results.append(
            CandidateResult(
                candidate_id=candidate.id,
                name=candidate.name,
                party=candidate.party,
                votes=candidate.votes,
                percentage=percentage,
            )
        )

    return VotingStatistics(
        total_voters_voted=total_voters_voted,
        results_by_candidate=results,
    )


def generate_votes_chart(db: Session) -> str:
    """
    Genera una gráfica de barras (Candidatos vs. Votos) usando Pandas + Matplotlib.
    Guarda el archivo en static/charts/voting_results.png y retorna la ruta.
    """
    candidates = db.query(Candidate).all()

    # Construir DataFrame de Pandas
    df = pd.DataFrame(
        [{"Candidato": c.name, "Votos": c.votes} for c in candidates],
        columns=["Candidato", "Votos"],
    )

    # Crear figura y graficar desde el DataFrame
    fig, ax = plt.subplots(figsize=(max(8, len(df) * 1.5), 6))
    bars = ax.bar(df["Candidato"], df["Votos"], color="steelblue", edgecolor="white")

    # Etiqueta numérica exacta sobre cada barra
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.1,
            str(int(height)),
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    ax.set_title("Resultados de Votación", fontsize=16, fontweight="bold")
    ax.set_xlabel("Candidatos", fontsize=12)
    ax.set_ylabel("Votos", fontsize=12)
    ax.set_ylim(bottom=0)
    plt.tight_layout()

    # Crear directorio si no existe y guardar imagen
    os.makedirs(CHART_DIR, exist_ok=True)
    fig.savefig(CHART_PATH, dpi=150)
    plt.close(fig)  # Liberar memoria

    return CHART_PATH
