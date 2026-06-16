import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import async_session
from app.models.filiere import Filiere
from app.models.recommendation import Recommandation
from app.models.user import User
from sqlalchemy import select
import json

def fix_text(text):
    if not isinstance(text, str):
        return text
    replacements = {
        "Ǹ": "é",
        "?": "É",
        "": "è",
        "ǩ": "î",
        "Ǧ": "ê"
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

def fix_json(data):
    if isinstance(data, list):
        return [fix_json(item) for item in data]
    elif isinstance(data, dict):
        return {k: fix_json(v) for k, v in data.items()}
    elif isinstance(data, str):
        return fix_text(data)
    return data

async def fix_database():
    print("Fixing database encoding issues...")
    async with async_session() as db:
        result = await db.execute(select(Filiere))
        filieres = result.scalars().all()
        for f in filieres:
            f.nom = fix_text(f.nom)
            f.domaine = fix_text(f.domaine)
            f.description = fix_text(f.description)
            f.niveau_entree = fix_text(f.niveau_entree)
            
            f.objectifs = fix_json(f.objectifs)
            f.competences_acquises = fix_json(f.competences_acquises)
            f.debouches = fix_json(f.debouches)
            f.etablissements = fix_json(f.etablissements)
            f.prerequis_academiques = fix_json(f.prerequis_academiques)
            f.temoignages = fix_json(f.temoignages)
            
        await db.commit()
        print("Fixed database!")

if __name__ == "__main__":
    asyncio.run(fix_database())
