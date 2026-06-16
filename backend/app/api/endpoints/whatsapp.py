from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from app.db.session import get_db
from app.models.conversation import Conversation
from app.services.llm_service import LLMService
from app.services.whatsapp_service import WhatsAppService

router = APIRouter()
llm_service = LLMService()
whatsapp_service = WhatsAppService()

@router.post("/webhook")
async def twilio_whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook appelé par Twilio lors de la réception d'un message WhatsApp
    """
    try:
        # Extraire les données du formulaire x-www-form-urlencoded
        form_data = await request.form()
        
        from_number = form_data.get("From")  # Ex: "whatsapp:+224620000000"
        body_text = form_data.get("Body", "").strip()
        
        if not from_number or not body_text:
            return {"status": "ignored", "reason": "Missing From or Body"}
            
        print(f"📥 Message WhatsApp reçu de {from_number}: {body_text}")
        
        # 1. Identifier la conversation par le numéro (on stocke le numéro comme user_id temp ou dans session_data)
        # Pour simplifier, on cherche une conversation active liée à ce numéro
        query = select(Conversation).filter(
            Conversation.session_data["whatsapp_number"].as_string() == from_number
        ).order_by(Conversation.updated_at.desc())
        
        result = await db.execute(query)
        conversation = result.scalars().first()
        
        if not conversation:
            # Nouvelle conversation WhatsApp
            conversation = Conversation(
                context_history=[],
                session_data={"whatsapp_number": from_number, "source": "whatsapp"}
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            
        # 2. Interroger LLM
        history = list(conversation.context_history)
        history.append({"role": "user", "content": body_text})
        
        ai_response = await llm_service.get_response(
            prompt=body_text,
            chat_history=history[:-1],
            db_session=db,
            session_data=conversation.session_data
        )
        
        history.append({"role": "assistant", "content": ai_response})
        conversation.context_history = history
        await db.commit()
        
        # 3. Répondre via Twilio API
        # On extrait juste le numéro sans le préfixe whatsapp: si nécessaire pour notre service
        # mais notre whatsapp_service.py le gère de toute façon.
        await whatsapp_service.send_message(from_number, ai_response)
        
        # Le webhook Twilio attend souvent une réponse TwiML vide ou texte ok
        return {"status": "success"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
