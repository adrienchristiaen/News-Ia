"""Brouillon de l'épisode à partir de la shortlist.

Deux voies :
 1. ANTHROPIC_API_KEY défini + `pip install -e ".[llm]"` → le brouillon est généré directement.
 2. Sinon, le prompt complet est écrit dans data/prompts/<semaine>.md : colle-le dans Claude,
    puis `newsia draft --response-file reponse.json` pour l'importer.

Dans tous les cas : c'est un BROUILLON. Tu relis, tu corriges les faits et tu réécris dans ton ton.
"""
from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path

from . import CONFIG, DATA, EPISODES
from .episode import MAX_SECONDS, validate
from .weeks import week_id

DEFAULT_MODEL = os.environ.get("NEWSIA_MODEL", "claude-sonnet-5-5")

SCHEMA = """{
  "id": "<semaine>", "title": "titre de l'épisode", "date": "AAAA-MM-JJ", "language": "fr",
  "hook": "accroche parlée (≤ 25 mots)",
  "segments": [
    {
      "id": "s1", "kicker": "MOT-CLÉ EN MAJUSCULES (ex. MODÈLES, RÉGULATION, OUTILS)",
      "headline": "titre court (≤ 8 mots)",
      "text": "voix off de la séquence (25-40 mots)",
      "stat": {"value": "chiffre clé tel que cité dans la source", "label": "ce que mesure ce chiffre"} ou null,
      "sources": [{"title": "...", "url": "...", "publisher": "..."}],
      "visual": {"kind": "engraving", "alt": "description d'une illustration de journal à créer"}
    }
  ],
  "outro": "phrase de clôture parlée (≤ 20 mots)",
  "social": {"caption": "légende de la publication", "hashtags": ["#IA", "..."]},
  "gazette": {
    "headline": "Une du journal", "lede": "chapeau (2 phrases)",
    "articles": [{"segment": "s1", "headline": "...", "body": ["paragraphe 1", "paragraphe 2"]}]
  }
}"""


def build_prompt(week: str) -> str:
    voice = (CONFIG / "voice.md").read_text()
    brand = json.loads((CONFIG / "brand.json").read_text())
    short = json.loads((DATA / "shortlist" / f"{week}.json").read_text())
    cands = "\n".join(
        f"{i+1}. [{c['score']}] {c['title']}\n   résumé : {c['summary'][:300]}\n   sources : "
        + " | ".join(f"{s['publisher']} <{s['url']}>" for s in c["sources"][:4])
        for i, c in enumerate(short["candidates"])
    )
    return f"""Tu rédiges le brouillon de l'épisode hebdomadaire « {brand['name']} » ({brand['tagline']}).

# Ton et règles de la chaîne
{voice}

# Contraintes dures
- Durée parlée totale ≤ {MAX_SECONDS} s (≈ 2,6 mots par seconde). Choisis 3 à 5 sujets parmi les candidats.
- N'affirme RIEN qui ne soit pas dans les sources listées. Si un chiffre n'est pas dans le résumé fourni, mets "stat": null.
- Chaque séquence cite au moins une source avec son URL exacte, reprise des candidats.
- Ne nomme jamais une personne réelle dans une illustration ou une description visuelle : décris des scènes symboliques.
- Réponds par UN SEUL objet JSON, sans texte autour, respectant ce schéma :

{SCHEMA}

# Candidats de la semaine {week} (déjà triés par pertinence)
{cands}
"""


def extract_json(text: str) -> dict:
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S) or re.search(r"(\{.*\})", text, re.S)
    if not m:
        raise ValueError("aucun JSON trouvé dans la réponse")
    return json.loads(m.group(1))


def call_api(prompt: str, model: str = DEFAULT_MODEL) -> str:
    try:
        import anthropic
    except ImportError as exc:
        raise SystemExit('SDK manquant : pip install -e "pipeline[llm]"') from exc
    msg = anthropic.Anthropic().messages.create(
        model=model, max_tokens=6000, messages=[{"role": "user", "content": prompt}]
    )
    return "".join(b.text for b in msg.content if b.type == "text")


def draft(week: str | None = None, response_file: Path | None = None, model: str = DEFAULT_MODEL) -> Path | None:
    week = week or week_id()
    prompt = build_prompt(week)
    ppath = DATA / "prompts" / f"{week}.md"
    ppath.parent.mkdir(parents=True, exist_ok=True)
    ppath.write_text(prompt)

    if response_file:
        raw = response_file.read_text()
    elif os.environ.get("ANTHROPIC_API_KEY"):
        print(f"→ génération via l'API ({model})…")
        raw = call_api(prompt, model)
    else:
        print(f"Pas de clé API : prompt écrit dans {ppath}\n"
              f"Colle-le dans Claude, enregistre la réponse JSON, puis : newsia draft --response-file reponse.json")
        return None

    ep = extract_json(raw)
    ep["id"] = week
    ep.setdefault("date", date.today().isoformat())
    ep.setdefault("language", "fr")
    out = EPISODES / week / "episode.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ep, ensure_ascii=False, indent=2))
    problems = validate(ep)
    print(f"→ brouillon écrit : {out}")
    for p in problems:
        print("  ", p)
    return out
