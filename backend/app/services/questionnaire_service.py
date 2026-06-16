from typing import Dict, Any, List

class QuestionnaireService:
    """
    Gère les étapes du questionnaire interactif d'orientation d'EduBot
    et convertit les réponses en profil structuré compatible avec le RecommendationEngine.
    """
    
    QUESTIONS = {
        1: {
            "title": "🎓 Série du Baccalauréat",
            "text": "Pour commencer, quelle est votre série de Baccalauréat ?",
            "options": [
                {"label": "Sciences Mathématiques (SM)", "value": "SM"},
                {"label": "Sciences Expérimentales (SE)", "value": "SE"},
                {"label": "Sciences Sociales (SS)", "value": "SS"}
            ]
        },
        2: {
            "title": "📊 Résultats Scolaires",
            "text": "Quelle est votre moyenne générale estimée ou réelle au Baccalauréat (sur 20) ? Et quelles sont vos deux matières préférées ou fortes ?",
            "placeholder": "Ex: 13.5/20, Mathématiques et Informatique"
        },
        3: {
            "title": "🎯 Vos Centres d'Intérêt (Profil RIASEC)",
            "text": "Parmi les activités suivantes, lesquelles vous correspondent le plus ? (Sélectionnez jusqu'à 3)",
            "options": [
                {"label": "🛠️ Manipuler des outils, concevoir ou démonter des objets (Réaliste)", "value": "R"},
                {"label": "🔬 Résoudre des problèmes scientifiques, analyser des faits (Investigateur)", "value": "I"},
                {"label": "🎨 Créer, dessiner, écrire ou jouer de la musique (Artiste)", "value": "A"},
                {"label": "🤝 Aider les gens, enseigner ou soigner les autres (Social)", "value": "S"},
                {"label": "💼 Diriger des projets, convaincre des clients, négocier (Entreprenant)", "value": "E"},
                {"label": "📁 Classer des documents, organiser des plannings (Conventionnel)", "value": "C"}
            ]
        },
        4: {
            "title": "💼 Aspirations Professionnelles",
            "text": "Dans quel secteur professionnel vous imaginez-vous travailler plus tard ?",
            "options": [
                {"label": "🏥 Santé & Médecine", "value": "sante"},
                {"label": "💻 Technologie & Informatique", "value": "ingenierie"},
                {"label": "⚖️ Droit & Justice", "value": "droit"},
                {"label": "📈 Commerce, Finance & Gestion", "value": "commerce"},
                {"label": "🏫 Éducation & Enseignement", "value": "education"},
                {"label": "🌾 Agriculture & Environnement", "value": "art"} # Simplifié pour le matching secteur
            ]
        },
        5: {
            "title": "📍 Contraintes Pratiques",
            "text": "Préférez-vous étudier obligatoirement à Conakry ou êtes-vous mobile dans toute la Guinée (Mamou, Boké, Labé, Kankan, Faranah) ? Quel est votre budget annuel maximum pour les études (en millions de GNF, facultatif) ?",
            "placeholder": "Ex: Mobile en Guinée, Budget: 5 millions GNF"
        }
    }
    
    @classmethod
    def get_step(cls, step_id: int) -> Dict[str, Any]:
        """Retourne la configuration de l'étape demandée"""
        return cls.QUESTIONS.get(step_id, {})
        
    @classmethod
    def parse_responses_to_profile(cls, answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prend les réponses textuelles/choisies et génère un profil structuré
        compatible avec le RecommendationEngine.
        """
        # Profil structuré par défaut
        profile = {
            "moyenne_generale": 10.0,
            "matieres_preferees": [],
            "aspirations": [],
            "budget_max": 100.0,  # En GNF divisé par 200 normalisé, ou par million
            "prefere_conakry": True,
            "duree_max_etudes": 5,
            "interets_holland": {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
        }
        
        # 1. Série de Bac
        bac_serie = answers.get("step_1", "SM")
        
        # 2. Moyenne et matières
        step_2_text = answers.get("step_2", "10")
        try:
            # Tenter d'extraire la moyenne du texte (ex: '13.5/20' ou '14')
            import re
            numbers = re.findall(r"\d+(?:\.\d+)?", step_2_text)
            if numbers:
                val = float(numbers[0])
                if val <= 20:
                    profile["moyenne_generale"] = val
        except Exception:
            pass
            
        # Extraire les matières préférées
        matieres_ref = ["mathematiques", "physique", "francais", "histoire", "economie", "biologie", "informatique", "anglais"]
        for matiere in matieres_ref:
            if matiere in step_2_text.lower() or (matiere[:4] in step_2_text.lower()):
                profile["matieres_preferees"].append(matiere)
                
        # 3. Profil RIASEC (Holland Codes)
        riasec_answers = answers.get("step_3", [])
        if isinstance(riasec_answers, str):
            riasec_answers = [riasec_answers]
            
        for code in riasec_answers:
            if code in profile["interets_holland"]:
                profile["interets_holland"][code] = 9.0  # Note élevée pour les intérêts choisis
                
        # 4. Aspirations
        aspiration_sector = answers.get("step_4", "ingenierie")
        profile["aspirations"] = [aspiration_sector]
        
        # 5. Contraintes pratiques (Conakry / Budget)
        step_5_text = answers.get("step_5", "Conakry").lower()
        if "mobile" in step_5_text or "region" in step_5_text or "toute" in step_5_text or "non" in step_5_text:
            profile["prefere_conakry"] = False
            
        # Essayer d'extraire le budget en millions de GNF
        try:
            import re
            budget_numbers = re.findall(r"\d+", step_5_text)
            if budget_numbers:
                # Convertir en GNF réels pour le matching (ex: '5' millions -> 5000000)
                profile["budget_max"] = float(budget_numbers[0]) * 1000000
        except Exception:
            pass
            
        return profile
