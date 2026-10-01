#!/usr/bin/env bash
# Prépare les fichiers à publier pour un épisode rendu : out/<semaine>/{tiktok,reels,shorts}.mp4 + légendes.
# Usage : scripts/export.sh 2026-w40
# TikTok, Instagram Reels et YouTube Shorts acceptent tous du 1080x1920 H.264 : un seul rendu,
# normalisé en volume (-14 LUFS, la cible des plateformes), copié sous trois noms.
set -euo pipefail
cd "$(dirname "$0")/.."
WEEK="${1:?Usage: scripts/export.sh 2026-w40}"
SRC="video/out/${WEEK}.mp4"
OUT="out/${WEEK}"
[[ -f "$SRC" ]] || { echo "✗ $SRC introuvable. Rends d'abord : (cd video && node render.mjs --week $WEEK)" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "✗ ffmpeg manquant (brew install ffmpeg)" >&2; exit 1; }
mkdir -p "$OUT"

HAS_AUDIO=$(ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 "$SRC" | head -1 || true)
if [[ -n "$HAS_AUDIO" ]]; then
  ffmpeg -y -loglevel error -i "$SRC" -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -movflags +faststart "$OUT/master.mp4"
else
  echo "⚠ pas de piste audio : export muet"
  cp "$SRC" "$OUT/master.mp4"
fi
for p in tiktok reels shorts; do cp "$OUT/master.mp4" "$OUT/$p.mp4"; done
rm "$OUT/master.mp4"

# Légende + hashtags prêts à coller, depuis episode.json
python3 - "$WEEK" "$OUT" <<'PY'
import json, sys
week, out = sys.argv[1:3]
ep = json.load(open(f"episodes/{week}/episode.json"))
soc = ep.get("social", {})
lines = [soc.get("caption", ep["title"]), "", " ".join(soc.get("hashtags", [])), "", "Sources :"]
for s in ep["segments"]:
    for src in s["sources"][:2]:
        lines.append(f"- {src['publisher']} : {src['url']}")
open(f"{out}/legende.txt", "w").write("\n".join(lines) + "\n")
PY
# La Gazette (site) réutilise la vidéo
mkdir -p "web/public/ep/${WEEK}" && cp "$OUT/shorts.mp4" "web/public/ep/${WEEK}/short.mp4"
echo "✓ $OUT : tiktok.mp4, reels.mp4, shorts.mp4, legende.txt"
