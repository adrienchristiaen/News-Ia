"""Calcule le minutage (timing.json) : quand chaque séquence et chaque mot apparaît.

Deux modes :
 - avec une voix off transcrite (words.json de `newsia transcribe`) : les mots du script
   sont calés sur ceux de la transcription (difflib) puis interpolés → sous-titres
   avec l'orthographe du script mais le rythme réel de ta voix ;
 - sans audio : estimation à ~2,6 mots/s (utile pour prévisualiser le template).
"""
from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path

from .episode import UNIT_PAUSE, WORDS_PER_SEC, units, words


def norm(w: str) -> str:
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)


def estimate(ep: dict) -> dict:
    t, out_words, out_units = 0.0, [], []
    for u in units(ep):
        start = t
        for w in words(u["text"]):
            dur = max(0.18, len(norm(w)) * 0.045 + 0.12) * (2.6 / WORDS_PER_SEC)
            out_words.append({"text": w, "start": round(t, 3), "end": round(t + dur, 3), "unit": u["id"]})
            t += dur
        out_units.append({"id": u["id"], "start": round(start, 3), "end": round(t, 3)})
        t += UNIT_PAUSE
    return {"mode": "estimate", "duration": round(t, 3), "units": out_units, "words": out_words}


def from_transcript(ep: dict, spoken: list[dict]) -> dict:
    script = [(w, u["id"]) for u in units(ep) for w in words(u["text"])]
    sn = [norm(w) for w, _ in script]
    tn = [norm(w["text"]) for w in spoken]
    anchors: dict[int, int] = {}
    for a, b, size in difflib.SequenceMatcher(None, sn, tn, autojunk=False).get_matching_blocks():
        for k in range(size):
            anchors[a + k] = b + k
    if not anchors:
        raise ValueError("aucun mot du script retrouvé dans la transcription : mauvais fichier audio ?")
    xs = sorted(anchors)
    mapped: list[int] = []
    for i in range(len(script)):
        if i in anchors:
            mapped.append(anchors[i])
            continue
        lo = max((x for x in xs if x < i), default=None)
        hi = min((x for x in xs if x > i), default=None)
        if lo is None:
            mapped.append(max(0, anchors[hi] - (hi - i)))
        elif hi is None:
            mapped.append(min(len(spoken) - 1, anchors[lo] + (i - lo)))
        else:
            frac = (i - lo) / (hi - lo)
            mapped.append(round(anchors[lo] + frac * (anchors[hi] - anchors[lo])))
    out_words = []
    for (w, uid), j in zip(script, mapped):
        j = min(max(j, 0), len(spoken) - 1)
        out_words.append({"text": w, "start": round(spoken[j]["start"], 3), "end": round(spoken[j]["end"], 3), "unit": uid})
    # une fin ne peut pas précéder un début ; on garde l'ordre croissant
    for prev, cur in zip(out_words, out_words[1:]):
        cur["start"] = max(cur["start"], prev["start"])
        cur["end"] = max(cur["end"], cur["start"] + 0.05)
    out_units = []
    for u in units(ep):
        ws = [w for w in out_words if w["unit"] == u["id"]]
        out_units.append({"id": u["id"], "start": ws[0]["start"], "end": ws[-1]["end"]})
    return {"mode": "transcript", "duration": round(spoken[-1]["end"] + 0.6, 3), "units": out_units, "words": out_words}


def align(ep: dict, words_json: Path | None) -> dict:
    if words_json and words_json.exists():
        return from_transcript(ep, json.loads(words_json.read_text()))
    return estimate(ep)
