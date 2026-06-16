from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

from app.db.session import get_db
from app.models.filiere import Filiere

router = APIRouter()

@router.get("", response_model=dict)
async def get_filieres(
    domaine: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère la liste des filières universitaires disponibles
    """
    query = select(Filiere)
    
    if domaine:
        query = query.where(Filiere.domaine.ilike(f"%{domaine}%"))
        
    if search:
        query = query.where(
            or_(
                Filiere.nom.ilike(f"%{search}%"),
                Filiere.description.ilike(f"%{search}%")
            )
        )
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    filieres = result.scalars().all()
    
    return {
        "success": True,
        "count": len(filieres),
        "data": [f.to_dict() for f in filieres]
    }

@router.get("/{filiere_id}", response_model=dict)
async def get_filiere(filiere_id: int, db: AsyncSession = Depends(get_db)):
    """
    Récupère les détails d'une filière spécifique
    """
    result = await db.execute(select(Filiere).where(Filiere.id == filiere_id))
    filiere = result.scalars().first()
    
    if not filiere:
        raise HTTPException(status_code=404, detail="Filière non trouvée")
        
    return {
        "success": True,
        "data": filiere.to_dict()
    }

@router.post("/compare", response_model=dict)
async def compare_filieres(filiere_ids: dict, db: AsyncSession = Depends(get_db)):
    """
    Compare plusieurs filières (envoi des ids dans {"filiere_ids": [1, 2]})
    """
    ids = filiere_ids.get("filiere_ids", [])
    if not ids or len(ids) < 2:
        raise HTTPException(status_code=400, detail="Veuillez fournir au moins 2 IDs à comparer")
        
    result = await db.execute(select(Filiere).where(Filiere.id.in_(ids)))
    filieres = result.scalars().all()
    
    return {
        "success": True,
        "data": [f.to_dict() for f in filieres]
    }
