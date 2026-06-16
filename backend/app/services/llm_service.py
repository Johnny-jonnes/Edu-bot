import json
import os
import urllib.request
import urllib.error
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.filiere import Filiere

class LLMService:
    """
    Service d'IA Generative connecte a Groq (Llama 3.1)
    Integre du RAG (Retrieval-Augmented Generation) pour l'orientation en Guinee.
    Prompt Systeme v2.0 - Reference : PROMPT-EDUBOT-2025-V2.0
    """

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
        self.model = "llama-3.3-70b-versatile"
        print(f"[LLM INIT] API Key: {self.api_key[:10]}... | Model: {self.model}")

    async def get_response(
        self,
        prompt: str,
        chat_history: List[Dict[str, str]] = None,
        db_session: AsyncSession = None,
        session_data: Dict[str, Any] = None
    ) -> str:
        """
        Interroge Groq en injectant le contexte de l'historique et des filieres (RAG).
        """
        if not self.api_key:
            return "[ERREUR CONFIG] Cle API Groq non trouvee. Contactez l'administrateur."

        chat_history = chat_history or []
        session_data = session_data or {}

        # 1. RAG : Recuperer des informations sur les filieres si pertinent
        filiere_context = ""
        if db_session:
            # Toujours injecter le contexte des filieres pour des reponses factuelles
            filiere_context = await self._build_filiere_context(db_session, prompt)

        # 2. Construire le prompt systeme v2.0
        system_prompt = self._build_system_prompt_v2(filiere_context, session_data)

        # 3. Formater les messages pour l'API
        messages = [{"role": "system", "content": system_prompt}]

        # Ajouter l'historique (limite aux 16 derniers messages pour le contexte de 20 echanges)
        for msg in chat_history[-16:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Ajouter le message utilisateur courant
        messages.append({"role": "user", "content": prompt})

        # 4. Envoyer la requete HTTP a Groq
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 1500
        }

        try:
            req = urllib.request.Request(
                self.API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "EduBot/1.0",
                },
                method="POST"
            )

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._send_request, req)

            response_json = json.loads(response)
            ai_message = response_json["choices"][0]["message"]["content"]
            return ai_message

        except urllib.error.HTTPError as e:
            error_data = e.read().decode("utf-8")
            print(f"[GROQ ERROR] HTTP {e.code} | Model: {self.model} | Response: {error_data[:300]}")
            
            if e.code == 429:
                return "Désolé, le service d'IA reçoit trop de demandes en ce moment (Limite API atteinte). Cependant, cette filière est un excellent choix qui offre de grandes opportunités en Guinée ! Veuillez réessayer dans quelques minutes pour une analyse complète avec votre profil académique."
                
            if e.code in [401, 403]:
                return "Desole, je rencontre un probleme technique temporaire. Le service IA est en cours de maintenance. Veuillez reessayer dans quelques instants."
                
            return f"Desole, je rencontre une difficulte technique (Erreur {e.code}). Veuillez reessayer dans un instant."
        except Exception as e:
            print(f"[LLM ERROR] {str(e)}")
            return "Une erreur inattendue est survenue. Veuillez reessayer."

    def _send_request(self, req: urllib.request.Request) -> str:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")

    async def _build_filiere_context(self, db: AsyncSession, user_query: str) -> str:
        """Recupere et formate les filieres de la BDD correspondant a la requete de l'etudiant"""
        try:
            result = await db.execute(select(Filiere))
            filieres = result.scalars().all()

            if not filieres:
                return ""

            # Mots-cles pertinents etendus
            keywords = [
                "filiere", "etude", "etudes", "droit", "medecine", "pharmacie",
                "informatique", "bac", "universite", "debouche", "insertion",
                "cout", "frais", "mines", "geologie", "agronomie", "veterinaire",
                "gestion", "economie", "lettres", "anglais", "sociologie",
                "philosophie", "psychologie", "biologie", "chimie", "physique",
                "mathematiques", "genie", "civil", "electrique", "peche",
                "journalisme", "communication", "sante", "commerce",
                "boke", "sonfonia", "conakry", "kankan", "faranah", "mamou",
                "nzerekore", "labe", "uganc", "uglcs", "ismgb", "isav",
                "orientation", "recommandation", "conseil", "formation",
                "licence", "master", "doctorat", "bts", "dut", "ingenieur"
            ]

            query_lower = prompt_normalize(user_query)
            has_keyword = any(k in query_lower for k in keywords)

            if has_keyword:
                matching = filieres  # Envoyer toutes les filieres pour que l'IA fasse le tri
            else:
                matching = filieres[:5]  # Par defaut, envoyer les 5 premieres

            # Limiter a 15 pour ne pas exploser le contexte
            matching = matching[:15]

            context_str = "\n=== CATALOGUE DES FILIERES DISPONIBLES EN GUINEE (base de donnees reelle) ===\n"
            for f in matching:
                etabs = ""
                try:
                    etabs = ', '.join([e.get('nom', '') + ' (' + e.get('ville', '') + ')' for e in (f.etablissements or [])])
                except:
                    etabs = "Non renseigne"

                prereqs = f.prerequis_academiques or {}
                context_str += (
                    f"\n--- {f.nom} ({f.domaine}) ---\n"
                    f"  Duree: {f.duree_annees} ans | Niveau requis: {f.niveau_entree}\n"
                    f"  Etablissements: {etabs}\n"
                    f"  Serie Bac requise: {prereqs.get('serie_bac', 'Non precise')}\n"
                    f"  Note minimum: {prereqs.get('note_seuil', 'Non precise')}/20\n"
                    f"  Matieres cles: {', '.join(getattr(f, 'matieres_cles', []) or [])}\n"
                    f"  Debouches: {', '.join(f.debouches or [])}\n"
                    f"  Taux insertion: {f.taux_insertion}%\n"
                    f"  Salaire moyen sortie: {int(f.salaire_moyen_sortie or 0):,} GNF/mois\n"
                    f"  Cout annuel: {int(getattr(f, 'cout_annuel_moyen', 0) or 0):,} GNF\n"
                )
            return context_str
        except Exception as e:
            print(f"[RAG ERROR] Chargement filieres: {e}")
            return ""

    def _build_system_prompt_v2(self, filiere_context: str, session_data: Dict[str, Any]) -> str:
        """
        Construit le prompt systeme v2.0 conforme au document PROMPT-EDUBOT-2025-V2.0
        """
        prompt = """Tu es EduBot, un conseiller d'orientation academique intelligent concu exclusivement pour le systeme educatif guineen.
Tu guides les eleves et etudiants vers les meilleures filieres disponibles EN GUINEE, en analysant leur releve de notes officiel et leur profil personnel.

IDENTITE :
- Langue principale : francais
- Comprehension partielle : Pular (Peul), Soussou, Malinke
- Tu es factuel, bienveillant, precis et ancre dans la realite guineenne
- Tu ne mentionnes que des etablissements, filieres, programmes et debouches qui existent reellement en Republique de Guinee

ROLE ACTUEL : ETUDIANT (par defaut)
Ton ton : Chaleureux, encourageant, pedagogique. Utilise "tu". Evite le jargon technique.
Si l'etudiant semble decourage, rassure-le et propose des alternatives realistes.

SERIES DU BACCALAUREAT GUINEEN :
| Code | Serie | Dominante |
| A | Lettres & Sciences Humaines | Philosophie, Francais, Histoire-Geo |
| B | Sciences Economiques & Sociales | Economie, Mathematiques |
| C | Mathematiques & Physique | Maths, Physique-Chimie |
| D | Sciences Biologiques | SVT, Chimie, Maths |
| E | Mathematiques & Technologie | Maths, Technologie |
| G1 | Comptabilite & Gestion | Comptabilite, Economie |
| G2 | Secretariat & Bureautique | Secretariat, Informatique |
| F | Technique Industrielle | Technologie, Physique |

UNIVERSITES PUBLIQUES DE GUINEE :
- UGANC (Universite Gamal Abdel Nasser de Conakry) : FST, FSSH, FDSP, FSEG, FLSL, FMPOS
- UGLCS (Universite General Lansana Conte de Sonfonia) : Droit, Economie, Lettres
- UJNK (Universite Julius Nyerere de Kankan) : Sciences, Lettres, Education
- UN (Universite de Nzerekore) : Sciences, Droit
- IPC (Institut Polytechnique de Conakry) : BTS Informatique, Genie Civil, Maintenance
- ISSEG (Institut Superieur des Sciences de l'Education) : Formation des enseignants
- ISMGB (Institut Superieur des Mines et Geologie de Boke) : Mines, Geologie
- ISAV (Institut Superieur Agronomique et Veterinaire de Faranah) : Agronomie, Elevage, Veterinaire
- ISSH (Institut Superieur des Sciences Halieutiques de Kamsar) : Peche, Aquaculture
- ENPT (Ecole Nationale des Postes et Telecommunications) : Telecoms, TIC
- ENCA (Ecole Nationale de Commerce et d'Administration) : Commerce, Gestion

DEBOUCHES PAR DOMAINE EN GUINEE :
- Medecine/Pharmacie : CHU Ignace Deen, CHU Donka, cliniques privees, MSF, OMS
- Informatique/TIC : Orange Guinee, MTN Guinee, startups tech Conakry
- Mines/Geologie : CBG, SMB, SAG, Rio Tinto Guinee
- Agronomie : IRAG, projets FAO/PNUD, SOGUIPAH
- Droit : Tribunaux, cabinets d'avocats, ministeres
- Economie/Gestion : BCRG, Ecobank, BICIGUI, UBA

FRAIS DE SCOLARITE (indicatifs 2024-2025, en GNF) :
- Universites publiques : 400 000 - 1 500 000 GNF/an
- Universites privees agreees : 3 000 000 - 8 000 000 GNF/an

CALCUL DU SCORE DE COMPATIBILITE (0-100) :
Score = (note_matieres_requises * 0.50) + (serie_bac_adequation * 0.25) + (mention_obtenue * 0.15) + (coherence_aspiration * 0.10)

REGLES ABSOLUES :
1. Ne JAMAIS donner de recommandations de filières tant que tu ne connais pas le profil de l'étudiant (série du bac, notes principales, ou intérêts précis).
2. Si un étudiant demande des filières sans se présenter, refuse poliment de lui faire une liste, et demande-lui plutôt de partager ses résultats scolaires ou de parler de ses passions.
3. Ne JAMAIS inventer d'établissements, filières ou programmes qui n'existent pas en Guinée.
4. Ne JAMAIS donner d'informations sur des universités étrangères sauf demande explicite.
5. Ne JAMAIS décourager un étudiant.
6. Ne JAMAIS garantir une admission (probabilités, pas certitudes).
7. Toujours proposer au minimum 3 alternatives (une fois le profil connu).
8. Être transparent sur le score de compatibilité.
9. Signaler si un document semble illisible ou non reconnu.

FORMAT DE REPONSE APRES ANALYSE DE RELEVE :
1. Resume de l'analyse (serie, etablissement, notes cles)
2. Top 3 recommandations avec scores
3. Prochaine etape proposee

ESCALADE VERS CONSEILLER HUMAIN si :
- L'etudiant exprime une detresse emotionnelle
- Le cas est complexe (reorientation apres echec, handicap)
- Aucune filiere compatible trouvee
- L'etudiant demande explicitement un humain

En cas d'incertitude : "D'apres mes donnees, [information]. Je te recommande de verifier directement aupres de [etablissement]."
"""

        if filiere_context:
            prompt += (
                "\n\nVoici les donnees REELLES du catalogue des filieres universitaires en Guinee "
                "issues de la base de donnees EduBot. Tu DOIS utiliser ces informations pour tes recommandations :\n"
                f"{filiere_context}\n"
            )

        # Gestion du questionnaire interactif
        is_questionnaire = session_data.get("is_in_questionnaire", False)
        current_step = session_data.get("questionnaire_step", 0)

        if is_questionnaire:
            prompt += (
                f"\n[QUESTIONNAIRE EN COURS - Etape {current_step}/5]\n"
                "Pose les questions une par une, de maniere douce et conversationnelle.\n"
            )
        else:
            prompt += (
                "\nConsignes de reponse :\n"
                "- Reponses concises (max 5-7 lignes pour un etudiant)\n"
                "- Utilise des puces et du gras pour structurer\n"
                "- Termine toujours par une question ou une proposition d'action\n"
                "- Si l'etudiant veut de l'aide, suggere d'importer son releve de notes ou de demarrer le questionnaire\n"
            )

        return prompt


def prompt_normalize(text: str) -> str:
    """Normalise un texte pour la recherche de mots-cles (retire accents basiques)"""
    replacements = {
        'e': 'e', 'e': 'e', 'a': 'a', 'i': 'i', 'o': 'o', 'u': 'u',
    }
    text = text.lower()
    for accent, plain in replacements.items():
        text = text.replace(accent, plain)
    return text
