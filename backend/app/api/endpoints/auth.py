from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.db.session import get_db
from app.models.user import User
from app.core.security import create_access_token, get_current_user
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user_data: dict, db: AsyncSession = Depends(get_db)):
    """
    Inscription d'un nouvel étudiant
    """
    email = user_data.get("email")
    password = user_data.get("password")
    full_name = user_data.get("full_name")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'email et le mot de passe sont requis"
        )
        
    # Vérifier si l'utilisateur existe déjà
    result = await db.execute(select(User).where(User.email == email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet e-mail est déjà enregistré"
        )
        
    # Créer l'utilisateur
    new_user = User(
        email=email,
        password_hash=User.get_password_hash(password),
        full_name=full_name,
        role="student",
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Créer le token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "success": True,
        "token": access_token,
        "user": new_user.to_dict(),
        "message": "Inscription réussie !"
    }

@router.post("/login", response_model=dict)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Connexion OAuth2 standard (renvoie un token de type Bearer)
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }

@router.get("/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Récupère les informations de l'utilisateur connecté
    """
    return {
        "success": True,
        "user": current_user.to_dict()
    }
