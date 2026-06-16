from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api.endpoints import chat, filieres, recommendation, auth, whatsapp, upload, admin
from app.core.config import settings
from app.db.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("[SUCCESS] Base de données initialisée")
    yield
    # Shutdown
    print("[SHUTDOWN] Application fermée")

app = FastAPI(
    title="EduBot API",
    description="Chatbot d'Orientation Académique - Guinée",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(filieres.router, prefix="/api/filieres", tags=["Filières"])
app.include_router(recommendation.router, prefix="/api/recommendation", tags=["Recommandation"])
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administration"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur EduBot API",
        "docs": "/docs",
        "redoc": "/redoc"
    }