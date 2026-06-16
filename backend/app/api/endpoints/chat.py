import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.services.llm_service import LLMService
from app.services.voice_service import VoiceService

router = APIRouter()
llm_service = LLMService()
voice_service = VoiceService()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@router.post("/send", response_model=dict)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    # Pour le mode visiteur, l'auth n'est pas strictement requise sur cette route publique
    # mais pour enregistrer l'historique de l'utilisateur on peut l'utiliser si dispo
):
    """
    Envoie un message textuel au chatbot et obtient une réponse générée par l'IA (Groq Llama 3)
    """
    try:
        user_message = request.message
        session_id = request.session_id
        
        # 1. Récupérer ou créer la conversation
        conversation = None
        if session_id:
            result = await db.execute(select(Conversation).where(Conversation.id == session_id))
            conversation = result.scalars().first()
            
        if not conversation:
            conversation = Conversation(
                context_history=[],
                session_data={}
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            
        # Ajouter le message de l'utilisateur à l'historique
        history = list(conversation.context_history)
        history.append({"role": "user", "content": user_message})
        
        # 2. Interroger le service LLM (Groq)
        ai_response = await llm_service.get_response(
            prompt=user_message,
            chat_history=history[:-1], # Envoyer l'historique avant le message courant
            db_session=db,
            session_data=conversation.session_data
        )
        
        # Ajouter la réponse IA à l'historique
        history.append({"role": "assistant", "content": ai_response})
        
        # Mettre à jour la conversation
        conversation.context_history = history
        await db.commit()
        
        return {
            "success": True,
            "session_id": conversation.id,
            "response": ai_response
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur du Chatbot: {str(e)}")

@router.post("/voice", response_model=dict)
async def send_voice_message(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Accepte un fichier audio, le transcrit via Whisper, puis l'envoie au Chatbot
    """
    try:
        # 1. Lire le fichier audio
        audio_content = await file.read()
        
        # 2. Transcrire avec Whisper
        transcription = await voice_service.transcribe_audio(audio_content, file.filename)
        
        if not transcription:
            raise HTTPException(status_code=400, detail="Impossible de transcrire le fichier audio.")
            
        # 3. Traiter comme un message texte normal
        request = ChatRequest(message=transcription, session_id=session_id)
        chat_response = await send_message(request, db)
        
        return {
            "success": True,
            "transcription": transcription,
            "session_id": chat_response.get("session_id"),
            "response": chat_response.get("response")
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur vocale: {str(e)}")

@router.get("/history", response_model=dict)
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère l'historique d'une conversation
    """
    result = await db.execute(select(Conversation).where(Conversation.id == session_id))
    conversation = result.scalars().first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation non trouvée")
        
    return {
        "success": True,
        "history": conversation.context_history
    }
