"""Déduplication, regroupement par sujet et classement.

Un sujet qui apparaît dans plusieurs sources indépendantes remonte (c'est le meilleur
signal que « c'est vraiment pertinent »). Aucune dépendance : similarité de Jaccard sur
les mots significatifs des titres.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone

from . import CONFIG, DATA

STOP = set("""le la les un une des du de d l et ou en au aux à a the of for to in on with and or is are
its it this that new how why what vs from by as at be can will has have""".split())


def tokens(title: str) -> set[str]:
    words = re.findall(r"[a-zà-ÿ0-9\-\.]+", title.lower())
    return {w for w in words if w not in STOP and len(w) > 2}


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def cluster(items: list[dict], threshold: float = 0.34) -> list[list[dict]]:
    clusters: list[tuple[set[str], list[dict]]] = []
    for it in items:
        tk = tokens(it["title"])
        for ctk, members in clusters:
            if jaccard(tk, ctk) >= threshold:
                members.append(it)
                ctk |= tk
                break
        else:
            clusters.append((set(tk), [it]))
    return [m for _, m in clusters]


def score(members: list[dict], kw: dict, now: datetime) -> float:
    sources = {m["source"] for m in members}
    best_weight = max(m["weight"] for m in members)
    s = 2.0 * best_weight + 3.0 * math.log2(1 + len(sources))
    text = " ".join(m["title"] + " " + m.get("summary", "") for m in members).lower()
    s += sum(1.0 for k in kw.get("boost", []) if k.lower() in text) * 0.6
    s -= sum(1.0 for k in kw.get("penalty", []) if k.lower() in text) * 2.0
    dates = [datetime.fromisoformat(m["published"]) for m in members if m.get("published")]
    if dates:
        age_days = (now - max(dates)).total_seconds() / 86400
        s += max(0.0, 3.0 - 0.4 * age_days)
    return round(s, 2)


def rank(week: str, top: int = 12, now: datetime | None = None) -> dict:
    raw = json.loads((DATA / "raw" / f"{week}.json").read_text())
    kw = json.loads((CONFIG / "sources.json").read_text()).get("keywords", {})
    now = now or datetime.now(timezone.utc)
    seen, items = set(), []
    for it in raw["items"]:                       # déduplication par URL
        if it["url"] and it["url"] not in seen and it["title"]:
            seen.add(it["url"])
            items.append(it)
    groups = cluster(items)
    ranked = []
    for g in groups:
        g.sort(key=lambda m: -m["weight"])
        ranked.append({
            "score": score(g, kw, now),
            "title": g[0]["title"],
            "summary": g[0]["summary"],
            "sources": [{"title": m["title"], "url": m["url"], "publisher": m["source"]} for m in g],
        })
    ranked.sort(key=lambda r: -r["score"])
    out = {"week": week, "candidates": ranked[:top]}
    path = DATA / "shortlist" / f"{week}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"→ {len(out['candidates'])} sujets retenus ({len(items)} articles, {len(groups)} sujets) dans {path}")
    return out
