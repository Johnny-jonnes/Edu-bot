from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os

from app.core.config import settings

# En développement local hors docker, si psycopg2/asyncpg n'est pas disponible ou qu'on n'a pas PG
# on peut utiliser sqlite asynchrone en installant aiosqlite, ou lever une exception claire.
DATABASE_URL = settings.async_database_url

# Si on détecte qu'on n'est pas sous docker et que postgres est inaccessible, on peut basculer sur sqlite.
if "postgresql" in DATABASE_URL and not os.environ.get("DATABASE_URL"):
    # Par défaut, si aucune variable n'est définie, on offre une compatibilité SQLite.
    DATABASE_URL = "sqlite+aiosqlite:///./edubot.db"

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dépendance FastAPI pour injecter la session de BDD"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialise la base de données (appelée au lifespan au démarrage)"""
    # En production, on utilise les migrations Alembic ou le script SQL d'initialisation de PostgreSQL.
    # Pour le premier démarrage, on peut forcer la création des tables si besoin.
    from app.models.filiere import Base
    from app.models.user import Base as UserBase
    from app.models.conversation import Base as ConvBase
    from app.models.recommendation import Base as RecBase
    
    async with engine.begin() as conn:
        # Crée les tables si elles n'existent pas
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(UserBase.metadata.create_all)
        await conn.run_sync(ConvBase.metadata.create_all)
        await conn.run_sync(RecBase.metadata.create_all)
