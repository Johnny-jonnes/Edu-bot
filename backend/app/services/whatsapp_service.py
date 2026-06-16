import os
import urllib.request
import urllib.parse
import urllib.error
import json
import base64
import asyncio
from typing import Optional

from app.core.config import settings

class WhatsAppService:
    """
    Service d'intégration WhatsApp via Twilio API.
    Permet d'envoyer des messages d'orientation personnalisés sur WhatsApp.
    """
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID or os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = settings.TWILIO_AUTH_TOKEN or os.environ.get("TWILIO_AUTH_TOKEN")
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER or os.environ.get("TWILIO_WHATSAPP_NUMBER") or "+14155238886"
        
        # Mode simulation si les clés par défaut sont utilisées
        self.is_simulated = (
            not self.account_sid 
            or self.account_sid.startswith("ACXXXXXXXXXXXXXXXX")
            or not self.auth_token 
            or "your_" in self.auth_token
        )
        
        if self.is_simulated:
            print("[SIMULATION] Twilio WhatsApp configuré en MODE SIMULATION (clés manquantes ou fictives)")

    async def send_message(self, to_number: str, body: str) -> bool:
        """
        Envoie un message WhatsApp à un numéro d'étudiant.
        to_number: format international (ex: '+224620123456')
        """
        # Formater les numéros pour WhatsApp
        formatted_to = to_number if to_number.startswith("whatsapp:") else f"whatsapp:{to_number}"
        formatted_from = self.from_number if self.from_number.startswith("whatsapp:") else f"whatsapp:{self.from_number}"
        
        if self.is_simulated:
            print(f"\n[SIMULATION WHATSAPP] Message envoyé à {to_number} :")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(body)
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
            return True
            
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        payload = {
            "To": formatted_to,
            "From": formatted_from,
            "Body": body
        }
        
        data = urllib.parse.urlencode(payload).encode("utf-8")
        
        # Encodage Basic Auth pour Twilio
        auth_str = f"{self.account_sid}:{self.auth_token}"
        auth_bytes = auth_str.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            method="POST"
        )
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._send_request, req)
            response_json = json.loads(response)
            print(f"[SUCCESS] Message WhatsApp envoyé avec succès via Twilio SID: {response_json.get('sid')}")
            return True
            
        except urllib.error.HTTPError as e:
            error_data = e.read().decode("utf-8")
            print(f"[ERROR] Erreur envoi WhatsApp Twilio HTTP: {e.code} - {error_data}")
            return False
        except Exception as e:
            print(f"[ERROR] Erreur générale envoi WhatsApp Twilio: {str(e)}")
            return False
            
    def _send_request(self, req: urllib.request.Request) -> str:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode("utf-8")
