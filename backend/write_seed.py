import os

content = """import os
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
            is_active=True
        )
        student = User(
            email="etudiant@gmail.com",
            password_hash=pwd_context.hash("student123"),
            full_name="Etudiant Test",
            role="student",
            is_active=True
        )
        db.add_all([admin, student])

        filieres = [
            Filiere(
                nom="Médecine Générale",
                domaine="Santé",
                description="La Faculté des Sciences et Techniques de la Santé forme les médecins généralistes de Guinée.",
                duree_annees=7,
                niveau_entree="Bac",
                objectifs=["Diagnostiquer des maladies", "Traiter des patients", "Prévenir des pathologies"],
                competences_acquises=["Anatomie", "Physiologie", "Sémiologie", "Pharmacologie"],
                debouches=["Médecin généraliste", "Médecin de santé publique", "Chercheur"],
                etablissements=[{"nom": "UGANC - Université Gamal Abdel Nasser", "ville": "Conakry", "type": "Public"}],
                prerequis_academiques={"serie_bac": "SE", "mention_min": "Bien", "note_seuil": 15},
                dossier_requis=["Attestation du Bac", "Orientation GUPOL", "Visite médicale"],
                date_limite_inscription=datetime(2026, 10, 30),
                taux_insertion=98.5,
                salaire_moyen_sortie=5000000.0,
                temoignages=[{"nom": "Fatoumata", "texte": "Les études sont longues mais sauver des vies n'a pas de prix."}],
                matieres_cles=["Biologie", "Chimie", "Physique"]
            ),
            Filiere(
                nom="Génie Informatique",
                domaine="Technologie",
                description="L'Institut Polytechnique forme les ingénieurs en développement, réseaux et cybersécurité.",
                duree_annees=5,
                niveau_entree="Bac",
                objectifs=["Concevoir des logiciels", "Gérer des réseaux", "Sécuriser des systèmes"],
                competences_acquises=["Algorithmique", "Développement Web", "Bases de données"],
                debouches=["Développeur Full-Stack", "Administrateur Réseaux", "Ingénieur IA"],
                etablissements=[{"nom": "UGANC - Institut Polytechnique", "ville": "Conakry", "type": "Public"}],
                prerequis_academiques={"serie_bac": "SM", "mention_min": "Assez Bien", "note_seuil": 13},
                dossier_requis=["Attestation du Bac", "Orientation GUPOL"],
                date_limite_inscription=datetime(2026, 10, 30),
                taux_insertion=90.0,
                salaire_moyen_sortie=6000000.0,
                temoignages=[{"nom": "Mamadou", "texte": "Le marché est très porteur avec la digitalisation de l'administration."}],
                matieres_cles=["Mathématiques", "Informatique", "Physique"]
            ),
            Filiere(
                nom="Licence Droit Privé",
                domaine="Droit",
                description="L'Université de Sonfonia forme les futurs juristes, avocats et magistrats du secteur privé.",
                duree_annees=3,
                niveau_entree="Bac",
                objectifs=["Analyser des contrats", "Défendre des clients", "Maîtriser le droit du travail"],
                competences_acquises=["Droit civil", "Droit pénal", "Droit des affaires"],
                debouches=["Avocat", "Juriste d'entreprise", "Notaire"],
                etablissements=[{"nom": "UGLC - Sonfonia", "ville": "Conakry", "type": "Public"}],
                prerequis_academiques={"serie_bac": "SS", "mention_min": "Passable", "note_seuil": 11},
                dossier_requis=["Attestation du Bac", "Orientation GUPOL"],
                date_limite_inscription=datetime(2026, 11, 5),
                taux_insertion=75.0,
                salaire_moyen_sortie=3000000.0,
                temoignages=[{"nom": "Aïssatou", "texte": "Formation indispensable pour comprendre et défendre nos droits."}],
                matieres_cles=["Français", "Philosophie", "Histoire"]
            ),
            Filiere(
                nom="Ingénieur Minier",
                domaine="Ingénierie",
                description="L'ISMGB forme l'élite de l'industrie minière guinéenne, au cœur du développement économique du pays.",
                duree_annees=5,
                niveau_entree="Bac",
                objectifs=["Explorer des gisements", "Exploiter des mines", "Gérer l'impact environnemental"],
                competences_acquises=["Géologie", "Topographie", "Mécanique des roches"],
                debouches=["Ingénieur d'exploitation", "Géologue", "Consultant minier"],
                etablissements=[{"nom": "ISMGB", "ville": "Boké", "type": "Public"}],
                prerequis_academiques={"serie_bac": "SM", "mention_min": "Bien", "note_seuil": 14},
                dossier_requis=["Attestation du Bac", "Orientation GUPOL", "Certificat médical"],
                date_limite_inscription=datetime(2026, 10, 30),
                taux_insertion=96.0,
                salaire_moyen_sortie=8000000.0,
                temoignages=[{"nom": "Ibrahima", "texte": "Obtenir ce diplôme à Boké, c'est l'assurance d'un emploi très bien rémunéré."}],
                matieres_cles=["Mathématiques", "Physique", "Chimie"]
            )
        ]
        
        db.add_all(filieres)
        await db.commit()

async def main():
    print("Initialisation de la base de donnees...")
    await init_db()
    print("Insertion des donnees...")
    await seed_data()
    print("Termine avec succes !")

if __name__ == "__main__":
    asyncio.run(main())
"""

with open("app/db/seed_db.py", "w", encoding="utf-8") as f:
    f.write(content)
print("seed_db.py rewritten with UTF-8 encoding.")
