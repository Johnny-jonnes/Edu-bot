import os
import json
import urllib.request
import urllib.error
import asyncio
from typing import Optional

from app.core.config import settings

class VoiceService:
    """
    Service de transcription vocale utilisant Groq Whisper (whisper-large-v3)
    Convertit des fichiers audio en texte en français.
    """
    
    API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
        self.model = "whisper-large-v3"
        
    async def transcribe_audio(self, file_content: bytes, filename: str) -> Optional[str]:
        """
        Transcrit un contenu audio (bytes) en texte via Groq Whisper.
        """
        if not self.api_key:
            print("[WARN] Cle API Groq non configuree pour la transcription")
            return None
            
        try:
            # Construction manuelle d'une requête multipart/form-data robuste
            boundary = "----WebKitFormBoundaryEduBotVoiceBoundary"
            
            mime_type = "audio/mpeg"
            if filename.endswith(".wav"):
                mime_type = "audio/wav"
            elif filename.endswith(".m4a"):
                mime_type = "audio/m4a"
            elif filename.endswith(".ogg"):
                mime_type = "audio/ogg"
            elif filename.endswith(".webm"):
                mime_type = "audio/webm"
                
            # Construire le corps multipart
            body = []
            
            # Champ model
            body.append(f"--{boundary}".encode('utf-8'))
            body.append('Content-Disposition: form-data; name="model"'.encode('utf-8'))
            body.append(''.encode('utf-8'))
            body.append(self.model.encode('utf-8'))
            
            # Champ language
            body.append(f"--{boundary}".encode('utf-8'))
            body.append('Content-Disposition: form-data; name="language"'.encode('utf-8'))
            body.append(''.encode('utf-8'))
            body.append('fr'.encode('utf-8'))
            
            # Fichier audio
            body.append(f"--{boundary}".encode('utf-8'))
            body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode('utf-8'))
            body.append(f'Content-Type: {mime_type}'.encode('utf-8'))
            body.append(''.encode('utf-8'))
            body.append(file_content)
            
            # Fin de la requête
            body.append(f"--{boundary}--".encode('utf-8'))
            body.append(''.encode('utf-8'))
            
            # Joindre les lignes avec \r\n
            data = b'\r\n'.join(body)
            
            req = urllib.request.Request(
                self.API_URL,
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                    "Content-Length": str(len(data)),
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EduBot/1.0"
                },
                method="POST"
            )
            
            # Exécuter l'appel réseau synchrone dans le threadpool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._send_request, req)
            
            response_json = json.loads(response)
            text = response_json.get("text", "")
            return text
            
        except urllib.error.HTTPError as e:
            error_data = e.read().decode("utf-8")
            print(f"[WHISPER ERROR] HTTP {e.code} - {error_data}")
            return None
        except Exception as e:
            print(f"[WHISPER ERROR] General: {str(e)}")
            return None
            
    def _send_request(self, req: urllib.request.Request) -> str:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")
