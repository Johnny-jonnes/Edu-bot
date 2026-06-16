# 🎓 EduBot - Documentation Technique & Architecture

Bienvenue dans la documentation technique du projet **EduBot**, le Chatbot d'Orientation Académique pour la Guinée.

## 🏗️ Architecture du Projet

Le projet repose sur une architecture moderne séparant clairement le frontend (interface utilisateur) du backend (logique métier et IA).

### 1. Frontend (Interface Utilisateur)
L'interface est développée avec les technologies suivantes :
- **Framework** : React.js via Vite (rapide et optimisé)
- **Routage** : React Router DOM (navigation fluide sans rechargement)
- **Style** : CSS Vanille (variables CSS complètes, design ultra premium, mode sombre, animations fluides)
- **Icônes** : Lucide React (icônes vectorielles professionnelles)
- **Principaux Composants** :
  - `ChatInterface.jsx` : L'interface conversationnelle avec l'IA, gérant le contexte et l'upload de relevés de notes.
  - `FilieresCatalog.jsx` : Le catalogue dynamique affichant les universités, filières avec un système de filtrage, barre de recherche et redirection vers le chat.
  - `Auth.jsx` : Interface de connexion / inscription.
  - `AdminDashboard.jsx` & `StudentDashboard.jsx` : Tableaux de bord personnalisés avec statistiques.

### 2. Backend (API & IA)
Le backend est une API robuste construite pour être asynchrone et performante :
- **Framework API** : FastAPI (Python) - *Choisi pour sa rapidité et sa gestion native de l'asynchrone*.
- **Base de données** : SQLite asynchrone (via `aiosqlite`) géré par SQLAlchemy (ORM).
- **Intelligence Artificielle (RAG)** :
  - **Groq API (Llama 3.3 70B)** : Le moteur LLM pour les réponses instantanées et intelligentes.
  - **LLMService** : Un service de RAG (Retrieval-Augmented Generation) qui injecte automatiquement les données réelles des filières de la base de données dans le prompt de l'IA.
  - **Gestion des Erreurs** : Fallback sécurisé en cas de "Rate Limit" (Erreur 429) de l'API Groq.
- **Fonctionnalités avancées** : 
  - OCR (Extraction de texte depuis les relevés de notes PDF/Images)
  - Intégration WhatsApp (via Twilio)
  - Système de recommandation algorithmique
  - Authentification JWT (JSON Web Tokens)

---

## 🚀 Comment lancer l'application en local ?

Pour faire fonctionner l'application, vous devez lancer **les deux serveurs en parallèle** (dans deux terminaux séparés).

> **Important:** Ouvrez deux fenêtres de terminal PowerShell pour effectuer ces actions en simultané.

### 🟢 1. Lancer le Backend (API Python)

Ouvrez un terminal (PowerShell) et exécutez ces commandes :

```powershell
# Aller dans le dossier backend
cd c:\Users\LUXE\Desktop\cms-edubot\backend

# Activer l'environnement virtuel Python
.\venv\Scripts\activate

# Lancer le serveur FastAPI avec rechargement automatique
uvicorn app.main:app --reload --port 8000
```
*Le backend sera accessible sur `http://localhost:8000`. L'interface de documentation Swagger de l'API est disponible sur `http://localhost:8000/docs`.*

### 🔵 2. Lancer le Frontend (React / Vite)

Ouvrez un **deuxième** terminal (PowerShell) et exécutez ces commandes :

```powershell
# Aller dans le dossier frontend
cd c:\Users\LUXE\Desktop\cms-edubot\frontend

# Lancer le serveur de développement Vite
npm run dev
```
*Le site web s'ouvrira sur `http://localhost:5173`.*

---

## 📂 Structure des Dossiers Importants

```text
cms-edubot/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/   # Routes de l'API (chat.py, filieres.py, auth.py)
│   │   ├── core/            # Configuration globale (config.py, security.py)
│   │   ├── db/              # Gestion de la BDD (session.py, seed_db.py)
│   │   ├── models/          # Modèles SQLAlchemy (user, filiere, conversation)
│   │   └── services/        # Logique métier (llm_service.py, ocr_service.py)
│   └── edubot.db            # Base de données SQLite
│
└── frontend/
    ├── src/
    │   ├── components/      # Composants React (chat, filieres, dashboard)
    │   ├── context/         # Contextes React (AuthContext)
    │   ├── services/        # Appels API vers le backend (api.js)
    │   ├── App.jsx          # Fichier racine et routage
    │   └── index.css        # Système de design global
    └── package.json         # Dépendances NPM
```

> **Note sur les Données :** La base de données a été remplie avec de véritables institutions guinéennes (UGANC, UGLC-S, ISMG, etc.) via le fichier `backend/app/db/seed_db.py`. Pour réinitialiser la BDD à tout moment, supprimez `edubot.db` et exécutez `python -m app.db.seed_db` depuis le dossier backend.
