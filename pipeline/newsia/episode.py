"""Chargement / validation d'un épisode (episodes/<id>/episode.json)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import EPISODES

WORDS_PER_SEC = 2.6          # débit de voix off français, posé
UNIT_PAUSE = 0.35            # silence entre deux séquences (s)
MAX_SECONDS = 90


class EpisodeError(ValueError):
    pass


def path_of(week: str) -> Path:
    return EPISODES / week / "episode.json"


def load(week_or_path: str) -> dict:
    p = Path(week_or_path)
    if not p.suffix:
        p = path_of(week_or_path)
    return json.loads(p.read_text())


def units(ep: dict) -> list[dict]:
    """Séquences lues à voix haute, dans l'ordre : accroche, séquences, clôture."""
    out = []
    if ep.get("hook"):
        out.append({"id": "hook", "text": ep["hook"]})
    out += [{"id": s["id"], "text": s["text"]} for s in ep["segments"]]
    if ep.get("outro"):
        out.append({"id": "outro", "text": ep["outro"]})
    return out


def words(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def estimated_seconds(ep: dict) -> float:
    us = units(ep)
    n = sum(len(words(u["text"])) for u in us)
    return n / WORDS_PER_SEC + UNIT_PAUSE * max(0, len(us) - 1)


def validate(ep: dict) -> list[str]:
    """Retourne la liste des problèmes (vide = OK). Les avertissements commencent par '⚠'."""
    errs: list[str] = []
    for key in ("id", "title", "date", "segments"):
        if not ep.get(key):
            errs.append(f"champ manquant : {key}")
    seen = set()
    for i, s in enumerate(ep.get("segments", [])):
        for key in ("id", "headline", "text"):
            if not s.get(key):
                errs.append(f"segments[{i}] : champ manquant « {key} »")
        if s.get("id") in seen:
            errs.append(f"segments[{i}] : id en double « {s.get('id')} »")
        seen.add(s.get("id"))
        if not s.get("sources"):
            errs.append(f"segments[{i}] ({s.get('id')}) : aucune source — on ne publie pas un fait sans source")
        for src in s.get("sources", []):
            if not str(src.get("url", "")).startswith("http"):
                errs.append(f"segments[{i}] : source sans URL valide")
    if ep.get("segments") and not errs:
        dur = estimated_seconds(ep)
        if dur > MAX_SECONDS:
            errs.append(f"⚠ durée estimée {dur:.0f}s > {MAX_SECONDS}s : coupe du texte")
    return errs
