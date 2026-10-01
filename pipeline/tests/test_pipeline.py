import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from newsia import align, collect, draft, episode, rank
import newsia

FIX = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 10, 2, tzinfo=timezone.utc)


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    for mod in (newsia, collect, rank, draft):
        monkeypatch.setattr(mod, "DATA", tmp_path / "data", raising=False)
    sources = tmp_path / "sources.json"
    sources.write_text(json.dumps({
        "lookbackDays": 8,
        "keywords": {"boost": ["open source", "benchmark", "regulation"], "penalty": ["sponsored", "webinar"]},
        "feeds": [{"name": "A", "url": str(FIX / "feed_a.xml"), "weight": 2},
                  {"name": "B", "url": str(FIX / "feed_b.xml"), "weight": 2},
                  {"name": "Cassé", "url": str(FIX / "nexiste_pas.xml"), "weight": 3}],
    }))
    return sources


def test_collect_skips_old_and_survives_broken_feed(sandbox):
    out = collect.collect("2026-w40", sandbox, NOW)
    titles = [i["title"] for i in out["items"]]
    assert len(out["items"]) == 4                      # l'article de 2024 est filtré
    assert not any("Vieille" in t for t in titles)
    assert [e["feed"] for e in out["errors"]] == ["Cassé"]


def test_rank_groups_same_story_and_demotes_promo(sandbox, monkeypatch):
    collect.collect("2026-w40", sandbox, NOW)
    monkeypatch.setattr(rank, "CONFIG", sandbox.parent)
    (sandbox.parent / "sources.json").write_text(sandbox.read_text())
    out = rank.rank("2026-w40", now=NOW)
    top = out["candidates"][0]
    assert "Orion" in top["title"] and len(top["sources"]) == 2   # deux sources → un seul sujet, en tête
    assert "Sponsored" in out["candidates"][-1]["title"]


def test_prompt_contains_rules_and_sources(sandbox, monkeypatch):
    collect.collect("2026-w40", sandbox, NOW)
    monkeypatch.setattr(rank, "CONFIG", sandbox.parent)
    (sandbox.parent / "sources.json").write_text(sandbox.read_text())
    rank.rank("2026-w40", now=NOW)
    p = draft.build_prompt("2026-w40")
    assert "N'affirme RIEN" in p and "https://example.com/a/orion" in p and "Ton et règles" in p


def test_extract_json_from_fenced_answer():
    assert draft.extract_json('Voilà :\n```json\n{"a": 1}\n```') == {"a": 1}


def demo():
    return json.loads((Path(newsia.EPISODES) / "demo-w00" / "episode.json").read_text())


def test_demo_episode_is_valid():
    assert [e for e in episode.validate(demo()) if not e.startswith("⚠")] == []


def test_validate_rejects_segment_without_source():
    ep = demo()
    ep["segments"][0]["sources"] = []
    assert any("aucune source" in e for e in episode.validate(ep))


def test_estimate_timing_is_monotonic_and_covers_all_words():
    ep = demo()
    t = align.estimate(ep)
    n = sum(len(episode.words(u["text"])) for u in episode.units(ep))
    assert len(t["words"]) == n
    assert all(a["end"] <= b["start"] + 1e-6 or a["unit"] != b["unit"] for a, b in zip(t["words"], t["words"][1:]))
    assert t["units"][0]["id"] == "hook" and t["units"][-1]["id"] == "outro"


def test_transcript_alignment_uses_real_timing_and_script_spelling():
    ep = demo()
    script = [w for u in episode.units(ep) for w in episode.words(u["text"])]
    # voix simulée : 0,4 s/mot, avec deux mots mal transcrits et un mot oublié
    spoken = [{"text": w.lower(), "start": i * 0.4, "end": i * 0.4 + 0.3} for i, w in enumerate(script)]
    spoken[5]["text"] = "xxx"; spoken[9]["text"] = "yyy"; del spoken[12]
    t = align.from_transcript(ep, spoken)
    assert [w["text"] for w in t["words"]] == script           # orthographe du script conservée
    starts = [w["start"] for w in t["words"]]
    assert starts == sorted(starts)
    assert abs(t["words"][20]["start"] - 20 * 0.4) < 0.9        # le rythme suit la voix
