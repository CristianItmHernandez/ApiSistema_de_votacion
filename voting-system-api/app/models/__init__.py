"""
Paquete de modelos ORM.
La importación explícita aquí garantiza que SQLAlchemy
registre todos los modelos antes de llamar a Base.metadata.create_all().
"""
from app.models.candidate import Candidate
from app.models.vote import Vote
from app.models.voter import Voter

__all__ = ["Voter", "Candidate", "Vote"]
