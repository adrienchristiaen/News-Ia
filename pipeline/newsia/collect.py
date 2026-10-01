"""Collecte des flux RSS/Atom → data/raw/<semaine>.json"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone

import feedparser

from . import CONFIG, DATA
from .weeks import week_id


def _entry_date(e) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        t = e.get(key)
        if t:
            return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
    return None


def fetch_feed(feed: dict, since: datetime) -> list[dict]:
    parsed = feedparser.parse(feed["url"], agent="news-ia/0.1 (+https://github.com/adrienchristiaen/News-Ia)")
    if parsed.bozo and not parsed.entries:
        raise RuntimeError(str(parsed.bozo_exception))
    items = []
    for e in parsed.entries:
        dt = _entry_date(e)
        if dt and dt < since:
            continue
        items.append({
            "title": (e.get("title") or "").strip(),
            "url": e.get("link", ""),
            "summary": (e.get("summary") or "").strip()[:600],
            "published": dt.isoformat() if dt else None,
            "source": feed["name"],
            "weight": feed.get("weight", 1),
        })
    return items


def collect(week: str | None = None, sources_file=None, now: datetime | None = None) -> dict:
    cfg = json.loads((sources_file or CONFIG / "sources.json").read_text())
    now = now or datetime.now(timezone.utc)
    since = now - timedelta(days=cfg.get("lookbackDays", 8))
    items, errors = [], []
    for feed in cfg["feeds"]:
        try:
            got = fetch_feed(feed, since)
            print(f"  ✓ {feed['name']}: {len(got)} articles")
            items += got
        except Exception as exc:  # un flux en panne ne doit pas bloquer la semaine
            print(f"  ✗ {feed['name']}: {exc}")
            errors.append({"feed": feed["name"], "error": str(exc)})
    week = week or week_id()
    out = {"week": week, "collectedAt": now.isoformat(), "items": items, "errors": errors}
    path = DATA / "raw" / f"{week}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f"→ {len(items)} articles écrits dans {path}")
    return out
