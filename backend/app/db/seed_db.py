# -*- coding: utf-8 -*-
import os
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user import User, Base as UserBase
from app.models.filiere import Filiere, Base as FiliereBase
from app.models.recommendation import Recommandation, Base as RecBase
from app.models.conversation import Base as ConvBase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE_URL = settings.async_database_url
if "postgresql" in DATABASE_URL and not os.environ.get("DATABASE_URL"):
    DATABASE_URL = "sqlite+aiosqlite:///./edubot.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(UserBase.metadata.drop_all)
        await conn.run_sync(FiliereBase.metadata.drop_all)
        await conn.run_sync(RecBase.metadata.drop_all)
        await conn.run_sync(ConvBase.metadata.drop_all)
        await conn.run_sync(UserBase.metadata.create_all)
        await conn.run_sync(FiliereBase.metadata.create_all)
        await conn.run_sync(RecBase.metadata.create_all)
        await conn.run_sync(ConvBase.metadata.create_all)


async def seed_data():
    async with AsyncSessionLocal() as db:
        admin = User(
            email="admin@edubot.gn",
            password_hash=pwd_context.hash("admin123"),
            full_name="Administrateur",
            role="admin",
            is_active=True,
        )
        student = User(
            email="etudiant@gmail.com",
            password_hash=pwd_context.hash("student123"),
            full_name="Etudiant Test",
            role="student",
            is_active=True,
        )
        db.add_all([admin, student])

        # Données basées sur le contexte des Universités Publiques et Privées en Guinée
        filieres_data = [
            # UGANC - Sciences
            {
                "nom": "Mathematiques",
                "domaine": "Sciences Exactes",
                "description": "Formation approfondie en mathematiques pures et appliquees a l'UGANC.",
                "duree_annees": 3,
                "niveau_entree": "Bac",
                "objectifs": ["Maitriser les concepts mathematiques", "Modeliser des problemes complexes", "Recherche fondamentale"],
                "competences_acquises": ["Analyse", "Algebre", "Probabilites", "Statistiques"],
                "debouches": ["Enseignant-chercheur", "Analyste quantitatif", "Data Scientist"],
                "etablissements": [{"nom": "UGANC", "ville": "Conakry", "type": "Public"}],
                "taux_insertion": 85.0,
            },
            {
                "nom": "Biologie",
                "domaine": "Sciences de la Vie",
                "description": "Etude du vivant, de la biologie cellulaire a l'ecologie.",
                "duree_annees": 3,
                "niveau_entree": "Bac",
                "objectifs": ["Comprendre les organismes vivants", "Realiser des analyses biologiques"],
                "competences_acquises": ["Microbiologie", "Genetique", "Biochimie"],
                "debouches": ["Biologiste", "Technicien de laboratoire", "Chercheur"],
                "etablissements": [{"nom": "UGANC", "ville": "Conakry", "type": "Public"}],
                "taux_insertion": 88.0,
            },
            # UGANC - Sante
            {
                "nom": "Medecine Generale",
                "domaine": "Sante",
                "description": "Formation de medecins generalistes pour le systeme de sante guineen a l'UGANC.",
                "duree_annees": 7,
                "niveau_entree": "Bac",
                "objectifs": ["Diagnostiquer", "Traiter", "Prevenir"],
                "competences_acquises": ["Anatomie", "Semiologie", "Pharmacologie"],
                "debouches": ["Medecin generaliste", "Specialiste", "Sante publique"],
                "etablissements": [{"nom": "UGANC", "ville": "Conakry", "type": "Public"}],
                "taux_insertion": 98.0,
            },
            {
                "nom": "Pharmacie",
                "domaine": "Sante",
                "description": "Formation en sciences pharmaceutiques, medicaments et sante publique.",
                "duree_annees": 6,
                "niveau_entree": "Bac",
                "objectifs": ["Formuler des medicaments", "Dispenser des traitements"],
                "competences_acquises": ["Chimie", "Pharmacognosie", "Toxicologie"],
                "debouches": ["Pharmacien d'officine", "Biologiste medical"],
                "etablissements": [{"nom": "UGANC", "ville": "Conakry", "type": "Public"}],
                "taux_insertion": 96.0,
            },
            {
                "nom": "Odontostomatologie",
                "domaine": "Sante",
                "description": "Chirurgie dentaire et medecine bucco-dentaire.",
                "duree_annees": 6,
                "niveau_entree": "Bac",
                "objectifs": ["Soins dentaires", "Chirurgie buccale"],
                "competences_acquises": ["Anatomie dentaire", "Parodontologie"],
                "debouches": ["Chirurgien-dentiste"],
                "etablissements": [{"nom": "UGANC", "ville": "Conakry", "type": "Public"}],
                "taux_insertion": 95.0,
            },
            # UGANC - Institut Polytechnique
            {
                "nom": "Genie Civil",
                "domaine": "Ingenierie",
                "description": "Formation d'ingenieurs batisseurs pour les infrastructures du pays.",
                "duree_annees": 5,
                "niveau_entree": "Bac",
                "objectifs": ["Concevoir", "Construire", "Superviser"],
                "competences_acquises": ["RDM", "Beton arme", "Topographie"],
                "debouches": ["Ingenieur BTP", "Chef de chantier", "Bureau d'etudes"],
                "etablissements": [{"nom": "UGANC", "ville": "Conakry", "type": "Public"}, {"nom": "Universite Roi Mohamed VI", "ville": "Conakry", "type": "Prive"}],
                "taux_insertion": 92.0,
            },
            {
                "nom": "Genie Electrique",
                "domaine": "Ingenierie",
                "description": "Systemes electriques, reseaux et energies.",
                "duree_annees": 5,
                "niveau_entree": "Bac",
                "objectifs": ["Conception electrique", "Maintenance", "Reseaux electriques"],
                "competences_acquises": ["Electrotechnique", "Electronique", "Automatisme"],
                "debouches": ["Ingenieur electricien", "Responsable maintenance"],
                "etablissements": [{"nom": "UGANC", "ville": "Conakry", "type": "Public"}, {"nom": "Universite Roi Mohamed VI", "ville": "Conakry", "type": "Prive"}],
                "taux_insertion": 90.0,
            },
            {
                "nom": "Telecommunications",
                "domaine": "Technologie",
                "description": "Reseaux et telecommunications.",
                "duree_annees": 5,
                "niveau_entree": "Bac",
                "objectifs": ["Gerer des reseaux", "Deployer la fibre/4G/5G"],
                "competences_acquises": ["Transmission", "Reseaux IP", "Securite"],
                "debouches": ["Ingenieur Telecom", "Architecte reseau"],
                "etablissements": [{"nom": "UGANC", "ville": "Conakry", "type": "Public"}, {"nom": "Universite Roi Mohamed VI", "ville": "Conakry", "type": "Prive"}],
                "taux_insertion": 94.0,
            },
            # Autres Instituts / Universites
            {
                "nom": "Sciences de l'Education",
                "domaine": "Sciences Humaines",
                "description": "Formation des futurs enseignants et cadres de l'education a l'ISSEG.",
                "duree_annees": 4,
                "niveau_entree": "Bac",
                "objectifs": ["Pedagogie", "Didactique", "Gestion de l'education"],
                "competences_acquises": ["Psychologie", "Sociologie", "Pratiques enseignantes"],
                "debouches": ["Professeur", "Inspecteur", "Conseiller pedagogique"],
                "etablissements": [{"nom": "ISSEG", "ville": "Conakry (Lambanyi)", "type": "Public"}],
                "taux_insertion": 82.0,
            },
            {
                "nom": "Agronomie et Elevage",
                "domaine": "Agriculture",
                "description": "Pour moderniser l'agriculture et l'elevage en Guinee.",
                "duree_annees": 5,
                "niveau_entree": "Bac",
                "objectifs": ["Production vegetale", "Production animale"],
                "competences_acquises": ["Zootechnie", "Phytotechnie", "Pedologie"],
                "debouches": ["Ingenieur agronome", "Veterinaire / Eleveur"],
                "etablissements": [{"nom": "ISAV", "ville": "Faranah", "type": "Public"}],
                "taux_insertion": 85.0,
            },
            {
                "nom": "Medecine Veterinaire",
                "domaine": "Sante Animale",
                "description": "Soins et sante des animaux d'elevage et de compagnie.",
                "duree_annees": 6,
                "niveau_entree": "Bac",
                "objectifs": ["Diagnostiquer", "Soigner les animaux"],
                "competences_acquises": ["Anatomie animale", "Chirurgie veterinaire"],
                "debouches": ["Docteur veterinaire", "Inspecteur sanitaire"],
                "etablissements": [{"nom": "ISSMV", "ville": "Dalaba", "type": "Public"}],
                "taux_insertion": 87.0,
            },
            {
                "nom": "Mines et Geologie",
                "domaine": "Ingenierie",
                "description": "Au coeur du developpement minier guineen a l'Institut Superieur de Boke.",
                "duree_annees": 5,
                "niveau_entree": "Bac",
                "objectifs": ["Exploration miniere", "Exploitation geologique"],
                "competences_acquises": ["Geophysique", "Mecanique des roches"],
                "debouches": ["Ingenieur minier", "Geologue", "Topographe"],
                "etablissements": [{"nom": "ISMG", "ville": "Boke", "type": "Public"}, {"nom": "Universite Roi Mohamed VI", "ville": "Conakry", "type": "Prive"}],
                "taux_insertion": 95.0,
            },
            {
                "nom": "Architecture et Urbanisme",
                "domaine": "Design et Environnement",
                "description": "Concevoir les villes et batiments de demain.",
                "duree_annees": 5,
                "niveau_entree": "Bac",
                "objectifs": ["Dessin architectural", "Planification urbaine"],
                "competences_acquises": ["Design 3D", "Urbanisme", "Materiaux"],
                "debouches": ["Architecte", "Urbaniste"],
                "etablissements": [{"nom": "ISAU", "ville": "Conakry", "type": "Public"}],
                "taux_insertion": 89.0,
            },
            {
                "nom": "Information et Communication",
                "domaine": "Lettres et Communication",
                "description": "Metiers du journalisme, des medias et de la communication institutionnelle.",
                "duree_annees": 3,
                "niveau_entree": "Bac",
                "objectifs": ["Informer", "Communiquer", "Maitriser les medias"],
                "competences_acquises": ["Redaction web", "Audiovisuel", "Relations publiques"],
                "debouches": ["Journaliste", "Charge de communication"],
                "etablissements": [{"nom": "ISIC", "ville": "Coyah", "type": "Public"}, {"nom": "Universite Roi Mohamed VI", "ville": "Conakry", "type": "Prive"}],
                "taux_insertion": 78.0,
            },
            {
                "nom": "Economie et Administration",
                "domaine": "Economie",
                "description": "Gestion, economie et administration des affaires.",
                "duree_annees": 3,
                "niveau_entree": "Bac",
                "objectifs": ["Gerer une entreprise", "Analyser l'economie"],
                "competences_acquises": ["Comptabilite", "Management", "Macroeconomie"],
                "debouches": ["Manager", "Comptable", "Economiste"],
                "etablissements": [{"nom": "ISCAEG", "ville": "Conakry", "type": "Public"}, {"nom": "UGLC-S", "ville": "Conakry", "type": "Public"}],
                "taux_insertion": 81.0,
            },
            # Universite Roi Mohamed VI specifiques
            {
                "nom": "Banque et Assurance",
                "domaine": "Finance",
                "description": "Formation pointue pour les metiers de la finance et de l'assurance.",
                "duree_annees": 3,
                "niveau_entree": "Bac",
                "objectifs": ["Maitriser les produits financiers", "Gestion des risques"],
                "competences_acquises": ["Finance d'entreprise", "Actuariat"],
                "debouches": ["Banquier", "Courtier", "Analyste risque"],
                "etablissements": [{"nom": "Universite Roi Mohamed VI", "ville": "Conakry", "type": "Prive"}],
                "taux_insertion": 88.0,
            },
        ]

        for f_data in filieres_data:
            filiere = Filiere(**f_data)
            db.add(filiere)

        await db.commit()


async def main():
    print("Initialisation de la base de donnees...")
    await init_db()
    print("Insertion des donnees avec universites (UGANC, UGLC-S, ISMG, etc.)...")
    await seed_data()
    print("Termine avec succes !")


if __name__ == "__main__":
    asyncio.run(main())
