"""Identifiants de semaine ISO, ex. 2026-w40."""
from datetime import date


def week_id(d: date | None = None) -> str:
    d = d or date.today()
    y, w, _ = d.isocalendar()
    return f"{y}-w{w:02d}"
