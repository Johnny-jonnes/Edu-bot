from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Filiere(Base):
    __tablename__ = "filieres"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(200), nullable=False, index=True)
    domaine = Column(String(100), nullable=False, index=True)  # Sciences, Lettres, Économie...
    description = Column(Text)
    duree_annees = Column(Integer)
    niveau_entree = Column(String(50))  # Bac, Bac+1, etc.
    objectifs = Column(JSON)  # Liste d'objectifs pédagogiques
    competences_acquises = Column(JSON)  # Liste de compétences
    debouches = Column(JSON)  # Débouchés professionnels
    etablissements = Column(JSON)  # Liste des établissements proposant
    
    # Conditions d'accès
    prerequis_academiques = Column(JSON)  # {serie_bac: "Série S", mention_min: "Assez Bien"}
    dossier_requis = Column(JSON)  # Liste des documents
    date_limite_inscription = Column(DateTime)
    
    # Métadonnées
    taux_insertion = Column(Float)  # %
    salaire_moyen_sortie = Column(Float)  # En GNF
    temoignages = Column(JSON)  # Liste de témoignages d'anciens étudiants
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Nouvelles colonnes
    profil_holland_recommande = Column(JSON)
    matieres_cles = Column(JSON)
    cout_annuel_moyen = Column(Float)
    
    # Relations
    recommandations = relationship("Recommandation", back_populates="filiere")
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nom": self.nom,
            "domaine": self.domaine,
            "description": self.description,
            "duree_annees": self.duree_annees,
            "niveau_entree": self.niveau_entree,
            "objectifs": self.objectifs,
            "competences_acquises": self.competences_acquises,
            "debouches": self.debouches,
            "etablissements": self.etablissements,
            "prerequis_academiques": self.prerequis_academiques,
            "dossier_requis": self.dossier_requis,
            "date_limite_inscription": self.date_limite_inscription.isoformat() if self.date_limite_inscription else None,
            "taux_insertion": self.taux_insertion,
            "salaire_moyen_sortie": self.salaire_moyen_sortie,
            "temoignages": self.temoignages,
        }