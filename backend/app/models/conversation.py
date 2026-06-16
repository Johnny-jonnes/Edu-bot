from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.models.filiere import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    # On utilise String(36) pour être compatible avec SQLite et Postgres (qui gère UUID natively ou via string)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_data = Column(JSON, default=dict)  # Stocke l'état courant (ex: étape du questionnaire)
    context_history = Column(JSON, default=list)  # Stocke la liste complète des messages [{"role": "user", "content": "..."}]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_data": self.session_data,
            "context_history": self.context_history,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
