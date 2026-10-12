#!/usr/bin/env python3
"""Assemble an IA Potter episode: template + episode JSON -> one self-contained HTML page.

Usage: python3 build.py episodes/s01e01.json   ->  dist/s01e01.html

Local media (media.src / media.poster pointing to a file under this folder, e.g. media/hat.webm)
is inlined as a data: URI, because the published page cannot load images or videos from other sites.
"""
import base64, json, mimetypes, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_INLINE = 4 * 1024 * 1024  # keep each clip small; the whole page must stay under 16 MB


def inline(value):
    if not isinstance(value, str) or value.startswith(("data:", "http://", "https://")):
        return value
    path = (ROOT / value).resolve()
    if not path.is_file():
        sys.exit(f"Média introuvable : {value}")
    data = path.read_bytes()
    if len(data) > MAX_INLINE:
        sys.exit(f"Média trop lourd ({len(data) // 1024} Ko) : {value}. Visez moins de 4 Mo.")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def walk(node):
    if isinstance(node, dict):
        if node.get("type") in ("video", "image"):
            for key in ("src", "poster"):
                if key in node:
                    node[key] = inline(node[key])
        for v in node.values():
            walk(v)
    elif isinstance(node, list):
        for v in node:
            walk(v)


def main():
    ep_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "episodes" / "s01e01.json"
    ep = json.loads(ep_path.read_text(encoding="utf-8"))
    walk(ep)
    sources = {s["id"] for s in ep.get("sources", [])}
    blob = json.dumps(ep, ensure_ascii=False)
    import re
    missing = sorted(set(re.findall(r"\[\^([\w-]+)\]", blob)) - sources)
    if missing:
        sys.exit(f"Citations sans source : {', '.join(missing)}")
    title = f"La Gazette du Codeur S{ep['season']:02d}EP{ep['episode']:02d}"
    html = (ROOT / "template" / "gazette.html").read_text(encoding="utf-8")
    html = html.replace("__TITLE__", title).replace("__EPISODE_JSON__", blob.replace("</", "<\\/"))
    out = ROOT / "dist" / f"s{ep['season']:02d}e{ep['episode']:02d}.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"{out}  ({len(html) // 1024} Ko)")


if __name__ == "__main__":
    main()
