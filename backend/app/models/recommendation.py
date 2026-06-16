from sqlalchemy import Column, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.filiere import Base

class Recommandation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filiere_id = Column(Integer, ForeignKey("filieres.id"), nullable=True)  # Lié à la filière principale recommandée si besoin
    profile_data = Column(JSON, nullable=False)  # Profil de l'étudiant (notes, intérêts)
    results = Column(JSON, nullable=False)  # Résultats complets [{filiere_id: X, score: Y, justification: Z}]
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="recommendations")
    filiere = relationship("Filiere", back_populates="recommandations")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filiere_id": self.filiere_id,
            "profile_data": self.profile_data,
            "results": self.results,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
