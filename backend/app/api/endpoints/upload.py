import fitz  # PyMuPDF
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any

from app.services.llm_service import LLMService

router = APIRouter()
llm_service = LLMService()

@router.post("/transcript", response_model=Dict[str, Any])
async def upload_transcript(file: UploadFile = File(...)):
    """
    Reçoit un fichier de relevé de notes (PDF), extrait le texte avec PyMuPDF,
    et utilise l'IA (Groq) pour extraire les matières et les notes.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Veuillez uploader un fichier PDF.")

    try:
        # Lire le fichier PDF en mémoire
        content = await file.read()
        
        # Extraire le texte avec PyMuPDF
        text = ""
        doc = fitz.open(stream=content, filetype="pdf")
        for page in doc:
            text += page.get_text()
            
        if not text.strip():
            raise HTTPException(status_code=400, detail="Impossible d'extraire le texte du PDF. Le document est peut-être scanné ou vide.")

        # Demander à l'LLM d'extraire les données JSON
        prompt = f"""
        Voici le texte extrait d'un document PDF :
        
        {text}
        
        Ta tâche est d'analyser ce document. S'il s'agit bien d'un relevé de notes scolaire ou universitaire, extrais les informations sous format JSON strict.
        Recherche en particulier :
        - La série du bac (si mentionnée, ex: "Sciences Expérimentales", "SM", "SE", "SS").
        - La mention obtenue (si mentionnée, ex: "Très Bien", "Bien", "Assez Bien", "Passable").
        - Les meilleures matières avec leurs notes (par exemple, Mathématiques: 16, Physique: 15, Français: 14).
        
        ATTENTION : Si le document N'EST CLAIREMENT PAS un relevé de notes (par exemple, un article, un roman, une facture), tu DOIS renvoyer le JSON avec un champ "error" expliquant le problème.
        
        Format JSON attendu EXCLUSIVEMENT (sans texte avant ou après) :
        {{
            "serie": "nom de la série ou null",
            "mention": "mention ou null",
            "notes": {{
                "Matière 1": 15,
                "Matière 2": 14
            }},
            "domaines_forts": ["domaine 1", "domaine 2"]
        }}
        
        Ou en cas de document invalide :
        {{
            "error": "Ce document ne semble pas être un relevé de notes scolaire."
        }}
        """
        
        ai_response = await llm_service.get_response(prompt=prompt, chat_history=[], db_session=None, session_data={})
        
        # Essayer de parser le JSON renvoyé
        try:
            # Nettoyer la réponse si elle contient des blocs de code markdown
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].strip()
                
            data = json.loads(ai_response)
            
            if "error" in data:
                raise HTTPException(status_code=400, detail=data["error"])
                
            # Vérifier si c'est vraiment un relevé de notes (il doit y avoir des notes)
            if not data.get("notes") or len(data.get("notes", {})) == 0:
                raise HTTPException(status_code=400, detail="Aucune note n'a pu être extraite. Veuillez vérifier que le document est un relevé de notes valide.")
                
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Impossible d'analyser le contenu du document.")
        except HTTPException as he:
            raise he

        return {
            "success": True,
            "data": data
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du document : {str(e)}")
