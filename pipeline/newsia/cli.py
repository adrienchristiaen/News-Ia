"""Interface en ligne de commande : `newsia <commande>`."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import EPISODES
from . import align as align_mod
from . import collect as collect_mod
from . import draft as draft_mod
from . import episode, rank as rank_mod
from .weeks import week_id


def main(argv=None):
    p = argparse.ArgumentParser(prog="newsia", description="Veille IA hebdomadaire → shorts + gazette")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, help_):
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("--week", default=None, help="ex. 2026-w40 (défaut : semaine courante)")
        return sp

    add("week", "affiche l'identifiant de la semaine courante")
    add("collect", "récupère les flux RSS")
    sp = add("rank", "classe les sujets de la semaine")
    sp.add_argument("--top", type=int, default=12)
    sp = add("draft", "génère (ou prépare le prompt du) brouillon d'épisode")
    sp.add_argument("--response-file", type=Path, default=None)
    sp.add_argument("--model", default=draft_mod.DEFAULT_MODEL)
    add("run", "collect + rank + draft d'un coup")
    add("validate", "vérifie episode.json (sources, durée…)")
    sp = add("transcribe", "transcrit episodes/<semaine>/voice.* → words.json")
    sp.add_argument("--model", default="small")
    add("align", "calcule timing.json (voix réelle si words.json existe, sinon estimation)")

    a = p.parse_args(argv)
    week = a.week or week_id()
    d = EPISODES / week

    if a.cmd == "week":
        print(week)
    elif a.cmd == "collect":
        collect_mod.collect(week)
    elif a.cmd == "rank":
        rank_mod.rank(week, a.top)
    elif a.cmd == "draft":
        draft_mod.draft(week, a.response_file, a.model)
    elif a.cmd == "run":
        collect_mod.collect(week)
        rank_mod.rank(week)
        draft_mod.draft(week)
    elif a.cmd == "validate":
        problems = episode.validate(episode.load(week))
        for pr in problems:
            print(pr)
        hard = [x for x in problems if not x.startswith("⚠")]
        print("✓ épisode valide" if not hard else f"✗ {len(hard)} problème(s)")
        raise SystemExit(1 if hard else 0)
    elif a.cmd == "transcribe":
        from .transcribe import transcribe
        audio = next(iter(sorted(d.glob("voice.*"))), None)
        if not audio:
            raise SystemExit(f"aucun fichier voice.* dans {d}")
        transcribe(audio, d / "words.json", a.model)
    elif a.cmd == "align":
        ep = episode.load(week)
        t = align_mod.align(ep, d / "words.json")
        (d / "timing.json").write_text(json.dumps(t, ensure_ascii=False, indent=1))
        print(f"→ {d/'timing.json'} (mode : {t['mode']}, durée : {t['duration']:.1f}s)")


if __name__ == "__main__":
    main()
