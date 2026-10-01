"""News IA — pipeline de veille hebdomadaire."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]      # racine du repo
CONFIG = ROOT / "config"
EPISODES = ROOT / "episodes"
DATA = ROOT / "data"                            # cache local, ignoré par git
