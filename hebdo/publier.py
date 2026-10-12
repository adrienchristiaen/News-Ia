#!/usr/bin/env python3
"""Publie le brouillon relu : passe son statut à « publie », valide, commit et pousse.

    python3 hebdo/publier.py              ->  le brouillon le plus récent
    python3 hebdo/publier.py 2026-10-19   ->  un numéro précis

Le push sur main déclenche le workflow GitHub Pages, qui met le site à jour.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(*cmd):
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT.parent)


def main():
    if len(sys.argv) > 1:
        path = ROOT / "numeros" / f"{sys.argv[1]}.json"
        if not path.exists():
            sys.exit(f"Numéro introuvable : {path.name}")
    else:
        brouillons = [p for p in sorted((ROOT / "numeros").glob("*.json"))
                      if json.loads(p.read_text(encoding="utf-8")).get("statut") == "brouillon"]
        if not brouillons:
            sys.exit("Aucun brouillon à publier. Lance d'abord : make gazette")
        path = brouillons[-1]
    n = json.loads(path.read_text(encoding="utf-8"))
    if n.get("statut") != "brouillon":
        sys.exit(f"{path.name} est déjà publié.")
    n["statut"] = "publie"
    path.write_text(json.dumps(n, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        run(sys.executable, "hebdo/build.py")
    except subprocess.CalledProcessError:
        n["statut"] = "brouillon"
        path.write_text(json.dumps(n, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        sys.exit("Le numéro ne passe pas la validation : il reste en brouillon.")
    run("git", "add", str(path.relative_to(ROOT.parent)))
    run("git", "commit", "-m", f"Gazette n°{n['numero']}, {n['date']}")
    run("git", "push")
    print(f"\nN° {n['numero']} publié. Le site se met à jour d'ici une à deux minutes.")


if __name__ == "__main__":
    main()
