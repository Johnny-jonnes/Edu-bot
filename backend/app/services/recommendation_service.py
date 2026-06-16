from typing import List, Dict, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

class RecommendationEngine:
    """
    Algorithme de matching profil-étudiant ↔ filière
    Basé sur un scoring pondéré multi-critères
    """
    
    # Poids des critères de recommandation
    CRITERIA_WEIGHTS = {
        "resultats_scolaires": 0.25,
        "matieres_preferees": 0.20,
        "aspirations_professionnelles": 0.20,
        "contraintes_pratiques": 0.15,  # lieu, budget, durée
        "interets_personnels": 0.12,
        "competences_existantes": 0.08,
    }
    
    def __init__(self, filieres_data: List[Dict]):
        self.filieres = filieres_data
        self.scaler = StandardScaler()
        
    def calculate_profile_vector(self, student_profile: Dict) -> np.ndarray:
        """
        Convertit le profil étudiant en vecteur numérique pour le matching
        """
        vector = []
        
        # 1. Résultats scolaires (normalisés 0-1)
        avg_grade = student_profile.get("moyenne_generale", 10) / 20
        vector.append(avg_grade)
        
        # 2. Matières préférées (one-hot encoding simplifié)
        matieres_pref = student_profile.get("matieres_preferees", [])
        matieres_ref = ["mathematiques", "physique", "francais", "histoire", 
                       "economie", "biologie", "informatique", "anglais"]
        for matiere in matieres_ref:
            vector.append(1 if matiere in matieres_pref else 0)
        
        # 3. Aspirations professionnelles
        aspirations = student_profile.get("aspirations", [])
        sectors = ["sante", "education", "ingenierie", "commerce", "droit", "art"]
        for sector in sectors:
            vector.append(1 if sector in aspirations else 0)
        
        # 4. Contraintes pratiques
        vector.append(student_profile.get("budget_max", 100) / 200)  # Normalisé
        vector.append(1 if student_profile.get("prefere_conakry", True) else 0)
        vector.append(student_profile.get("duree_max_etudes", 5) / 7)  # Normalisé
        
        # 5. Intérêts personnels (Holland Codes simplifié)
        interests = student_profile.get("interets_holland", {})
        for code in ["R", "I", "A", "S", "E", "C"]:
            vector.append(interests.get(code, 0) / 10)
        
        return np.array(vector)
    
    def calculate_filiere_vector(self, filiere: Dict) -> np.ndarray:
        """
        Convertit une filière en vecteur pour comparaison
        """
        vector = []
        
        # Niveau académique requis
        niveau_requis = filiere.get("prerequis_academiques", {})
        mention_map = {"Passable": 0.5, "Assez Bien": 0.7, "Bien": 0.85, "Très Bien": 1.0}
        vector.append(mention_map.get(niveau_requis.get("mention_min", "Passable"), 0.5))
        
        # Matières importantes pour la filière
        matieres_ref = ["mathematiques", "physique", "francais", "histoire", 
                       "economie", "biologie", "informatique", "anglais"]
        matieres_import = filiere.get("matieres_cles", [])
        for matiere in matieres_ref:
            vector.append(1 if matiere in matieres_import else 0)
        
        # Secteur professionnel ciblé
        secteurs = ["sante", "education", "ingenierie", "commerce", "droit", "art"]
        debouches = " ".join(filiere.get("debouches", [])).lower()
        for secteur in secteurs:
            vector.append(1 if secteur in debouches else 0)
        
        # Coût et localisation
        vector.append(filiere.get("cout_annuel_moyen", 100) / 200)
        vector.append(1 if "Conakry" in str(filiere.get("etablissements", [])) else 0)
        vector.append(filiere.get("duree_annees", 3) / 7)
        
        # Profil Holland cible
        holland_cible = filiere.get("profil_holland_recommande", {})
        for code in ["R", "I", "A", "S", "E", "C"]:
            vector.append(holland_cible.get(code, 0) / 10)
        
        return np.array(vector)
    
    def get_recommendations(
        self, 
        student_profile: Dict, 
        top_n: int = 3,
        min_score: float = 0.6
    ) -> List[Dict]:
        """
        Génère les recommandations de filières pour un étudiant
        """
        profile_vector = self.calculate_profile_vector(student_profile)
        
        recommendations = []
        
        for filiere in self.filieres:
            filiere_vector = self.calculate_filiere_vector(filiere)
            
            # Similarité cosinus pour le matching
            similarity = cosine_similarity(
                [profile_vector], 
                [filiere_vector]
            )[0][0]
            
            # Ajustement avec les poids des critères
            weighted_score = self._apply_criteria_weights(
                similarity, student_profile, filiere
            )
            
            if weighted_score >= min_score:
                recommendations.append({
                    "filiere": filiere,
                    "score": round(weighted_score * 100, 1),
                    "justification": self._generate_justification(
                        student_profile, filiere, weighted_score
                    )
                })
        
        # Tri par score décroissant
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:top_n]
    
    def _apply_criteria_weights(
        self, 
        base_score: float, 
        profile: Dict, 
        filiere: Dict
    ) -> float:
        """
        Ajuste le score de base avec les poids des critères personnalisés
        """
        adjusted_score = base_score
        
        # Bonus si les matières préférées correspondent aux matières clés
        matieres_pref = set(profile.get("matieres_preferees", []))
        matieres_cles = set(filiere.get("matieres_cles", []))
        if matieres_pref & matieres_cles:
            adjusted_score += 0.1 * len(matieres_pref & matieres_cles) / len(matieres_cles or [1])
        
        # Pénalité si budget insuffisant
        if profile.get("budget_max", 999) < filiere.get("cout_annuel_moyen", 0):
            adjusted_score *= 0.8
        
        return min(adjusted_score, 1.0)  # Cap à 1.0
    
    def _generate_justification(
        self, 
        profile: Dict, 
        filiere: Dict, 
        score: float
    ) -> str:
        """
        Génère une explication humaine de la recommandation
        """
        reasons = []
        
        if profile.get("moyenne_generale", 0) >= filiere.get("prerequis_academiques", {}).get("note_seuil", 0):
            reasons.append("✅ Vos résultats correspondent aux critères d'admission")
        
        matieres_communes = set(profile.get("matieres_preferees", [])) & set(filiere.get("matieres_cles", []))
        if matieres_communes:
            reasons.append(f"📚 Vos matières préférées ({', '.join(matieres_communes)}) sont centrales dans cette formation")
        
        if score >= 0.85:
            reasons.append("🎯 Excellente adéquation avec votre profil et vos aspirations")
        elif score >= 0.7:
            reasons.append("👍 Bonne correspondance avec vos intérêts et compétences")
        
        return " | ".join(reasons) if reasons else "Cette filière pourrait correspondre à votre profil"