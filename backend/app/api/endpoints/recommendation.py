from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.filiere import Filiere
from app.models.recommendation import Recommandation
from app.services.recommendation_service import RecommendationEngine
from app.services.pdf_generator import generate_recommendation_pdf

router = APIRouter()

@router.post("/generate", response_model=dict)
async def generate_recommendation(
    profile_data: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Génère des recommandations de filières basées sur le profil étudiant
    """
    try:
        # Récupérer toutes les filières (idéalement avec un cache ou un filtre initial)
        result = await db.execute(select(Filiere))
        filieres = result.scalars().all()
        
        # Convertir les objets SQLAlchemy en dictionnaires pour le moteur
        filieres_data = [f.to_dict() for f in filieres]
        
        # Initialiser le moteur de recommandation
        engine = RecommendationEngine(filieres_data)
        
        # Générer les recommandations
        recommendations = engine.get_recommendations(
            student_profile=profile_data,
            top_n=3,
            min_score=0.4 # Abaissé un peu pour être sûr d'avoir des résultats
        )
        
        # Sauvegarder l'historique
        main_filiere_id = recommendations[0]["filiere"]["id"] if recommendations else None
        
        new_rec = Recommandation(
            user_id=current_user.id,
            filiere_id=main_filiere_id,
            profile_data=profile_data,
            results=recommendations,
            created_at=datetime.utcnow()
        )
        db.add(new_rec)
        await db.commit()
        await db.refresh(new_rec)
        
        return {
            "success": True,
            "recommendation_id": new_rec.id,
            "recommendations": recommendations,
            "message": f"{len(recommendations)} filières recommandées"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de recommandation: {str(e)}")

@router.post("/generate/pdf", response_model=dict)
async def generate_recommendation_pdf_endpoint(
    recommendation_data: dict,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Génère un PDF téléchargeable des recommandations
    """
    try:
        # Générer le PDF asynchrone (ou synchrone wrappé)
        pdf_filename = await generate_recommendation_pdf(
            user_name=current_user.full_name or current_user.email,
            recommendations=recommendation_data,
            generated_at=datetime.utcnow()
        )
        
        return {
            "success": True,
            "pdf_url": f"/downloads/{pdf_filename}",
            "message": "PDF généré avec succès"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur PDF: {str(e)}")

@router.get("/history", response_model=dict)
async def get_recommendation_history(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère l'historique des recommandations de l'utilisateur
    """
    query = select(Recommandation).where(Recommandation.user_id == current_user.id).order_by(Recommandation.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    recs = result.scalars().all()
    
    return {
        "success": True,
        "data": [r.to_dict() for r in recs]
    }