"""
Punto de entrada de la aplicación FastAPI.
Registra los routers y crea las tablas al iniciar.
"""
from fastapi import FastAPI

import app.models  # Necesario para que SQLAlchemy registre todos los modelos
from app.database import Base, engine
from app.routers import candidates, voters, votes

# Crear tablas automáticamente al iniciar (constitution §1, criterio DoD Fase 1)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Votaciones API",
    description="API REST para gestión de votantes, candidatos y emisión de votos.",
    version="1.0.0",
)

app.include_router(voters.router)
app.include_router(candidates.router)
app.include_router(votes.router)


@app.get("/", tags=["Root"])
def root() -> dict:
    """Health check del servicio."""
    return {"status": "ok", "message": "Sistema de Votaciones API funcionando correctamente."}
