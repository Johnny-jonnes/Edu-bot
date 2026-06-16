-- PostgreSQL Schema for EduBot

-- Table: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(50) DEFAULT 'student', -- student, counselor, admin
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Table: filieres
CREATE TABLE filieres (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL,
    domaine VARCHAR(100) NOT NULL,
    description TEXT,
    duree_annees INTEGER,
    niveau_entree VARCHAR(50),
    objectifs JSONB,
    competences_acquises JSONB,
    debouches JSONB,
    etablissements JSONB,
    prerequis_academiques JSONB,
    dossier_requis JSONB,
    date_limite_inscription TIMESTAMP,
    taux_insertion FLOAT,
    salaire_moyen_sortie FLOAT,
    temoignages JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_filieres_domaine ON filieres(domaine);
CREATE INDEX idx_filieres_nom ON filieres(nom);
CREATE INDEX idx_filieres_niveau ON filieres(niveau_entree);

-- Table: conversations
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    session_data JSONB,
    context_history JSONB[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Table: recommendations
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    profile_data JSONB NOT NULL,
    results JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: feedback
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    recommendation_id INTEGER REFERENCES recommendations(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: admin_logs
CREATE TABLE admin_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES users(id),
    action VARCHAR(100),
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);