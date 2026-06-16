from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.filiere import Filiere
from app.core.security import get_current_user

router = APIRouter()


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Verifie que l'utilisateur connecte est un administrateur."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces reserve aux administrateurs"
        )
    return current_user


# ─── Stats ────────────────────────────────────────────────────────
@router.get("/stats", response_model=dict)
async def get_stats(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Renvoie les statistiques globales de la plateforme."""
    total_users = (await db.execute(func.count(User.id))).scalar() or 0
    total_filieres = (await db.execute(func.count(Filiere.id))).scalar() or 0
    active_users = (await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )).scalar() or 0
    admins = (await db.execute(
        select(func.count(User.id)).where(User.role == "admin")
    )).scalar() or 0
    students = (await db.execute(
        select(func.count(User.id)).where(User.role == "student")
    )).scalar() or 0

    return {
        "success": True,
        "data": {
            "total_users": total_users,
            "total_filieres": total_filieres,
            "active_users": active_users,
            "admins": admins,
            "students": students,
        }
    }


# ─── Users ────────────────────────────────────────────────────────
@router.get("/users", response_model=dict)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Liste tous les utilisateurs (pagine)."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return {
        "success": True,
        "count": len(users),
        "data": [u.to_dict() for u in users]
    }


@router.put("/users/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: int,
    body: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Change le role d'un utilisateur."""
    new_role = body.get("role")
    if new_role not in ("student", "admin"):
        raise HTTPException(status_code=400, detail="Role invalide (student ou admin)")

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalars().first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")

    target.role = new_role
    await db.commit()
    return {"success": True, "message": f"Role mis a jour vers {new_role}", "data": target.to_dict()}


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Supprime un utilisateur. Un admin ne peut pas se supprimer lui-meme."""
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte")

    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalars().first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")

    await db.delete(target)
    await db.commit()
    return {"success": True, "message": "Utilisateur supprime"}


# ─── Filieres CRUD ────────────────────────────────────────────────
@router.post("/filieres", response_model=dict)
async def create_filiere(
    body: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Cree une nouvelle filiere."""
    filiere = Filiere(
        nom=body.get("nom"),
        domaine=body.get("domaine"),
        description=body.get("description", ""),
        duree_annees=body.get("duree_annees", 3),
        niveau_entree=body.get("niveau_entree", "Bac"),
        objectifs=body.get("objectifs", []),
        competences_acquises=body.get("competences_acquises", []),
        debouches=body.get("debouches", []),
        etablissements=body.get("etablissements", []),
        prerequis_academiques=body.get("prerequis_academiques", {}),
        dossier_requis=body.get("dossier_requis", []),
        taux_insertion=body.get("taux_insertion", 0),
        salaire_moyen_sortie=body.get("salaire_moyen_sortie", 0),
        matieres_cles=body.get("matieres_cles", []),
        cout_annuel_moyen=body.get("cout_annuel_moyen", 0),
    )
    db.add(filiere)
    await db.commit()
    await db.refresh(filiere)
    return {"success": True, "message": "Filiere creee", "data": filiere.to_dict()}


@router.put("/filieres/{filiere_id}", response_model=dict)
async def update_filiere(
    filiere_id: int,
    body: dict,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Met a jour une filiere existante."""
    result = await db.execute(select(Filiere).where(Filiere.id == filiere_id))
    filiere = result.scalars().first()
    if not filiere:
        raise HTTPException(status_code=404, detail="Filiere non trouvee")

    updatable = [
        "nom", "domaine", "description", "duree_annees", "niveau_entree",
        "objectifs", "competences_acquises", "debouches", "etablissements",
        "prerequis_academiques", "dossier_requis", "taux_insertion",
        "salaire_moyen_sortie", "matieres_cles", "cout_annuel_moyen", "temoignages",
    ]
    for field in updatable:
        if field in body:
            setattr(filiere, field, body[field])

    filiere.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(filiere)
    return {"success": True, "message": "Filiere mise a jour", "data": filiere.to_dict()}


@router.delete("/filieres/{filiere_id}", response_model=dict)
async def delete_filiere(
    filiere_id: int,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Supprime une filiere."""
    result = await db.execute(select(Filiere).where(Filiere.id == filiere_id))
    filiere = result.scalars().first()
    if not filiere:
        raise HTTPException(status_code=404, detail="Filiere non trouvee")

    await db.delete(filiere)
    await db.commit()
    return {"success": True, "message": "Filiere supprimee"}


# ─── Export ───────────────────────────────────────────────────────
@router.get("/export/filieres", response_model=dict)
async def export_filieres(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Exporte toutes les filieres sous forme JSON."""
    result = await db.execute(select(Filiere))
    filieres = result.scalars().all()
    return {
        "success": True,
        "count": len(filieres),
        "data": [f.to_dict() for f in filieres]
    }
