"""Transcription locale de la voix off → words.json (mot, début, fin).

Nécessite : pip install -e ".[speech]"   (faster-whisper ; tourne sur CPU, ~1x temps réel sur un M1)
"""
from __future__ import annotations

import json
from pathlib import Path


def transcribe(audio: Path, out: Path, model: str = "small", language: str = "fr") -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit('faster-whisper manquant : pip install -e "pipeline[speech]"') from exc
    wm = WhisperModel(model, compute_type="int8")
    segments, _ = wm.transcribe(str(audio), language=language, word_timestamps=True, vad_filter=True)
    spoken = [{"text": w.word.strip(), "start": w.start, "end": w.end} for s in segments for w in (s.words or [])]
    out.write_text(json.dumps(spoken, ensure_ascii=False, indent=1))
    print(f"→ {len(spoken)} mots transcrits dans {out}")
    return spoken
