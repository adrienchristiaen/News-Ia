#!/usr/bin/env python3
"""Version e-mail (Gmail) et message Google Chat d'un épisode, avec le même design que la page.

Usage : python3 build_email.py episodes/s01e01.json
Produit :
  dist/s01e01-email.html   e-mail en tableaux HTML + styles en ligne, images intégrées (data:)
  dist/s01e01-chat.txt     message Google Chat (texte mis en forme)
  dist/email-assets/       les images (PNG, GIF) pour les héberger ou les joindre

Prérequis : python3 build.py (la page dist/s01e01.html doit exister), playwright, Pillow.
Gmail ignore JavaScript, polices web, SVG et animations CSS : les titres sont donc des images,
l'illustration animée est un GIF, le reste est du vrai texte.
"""
import base64, html, io, json, os, re, sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
# Chromium : variable GAZETTE_CHROME, sinon celui du conteneur cloud s'il existe, sinon celui de Playwright
_cloud = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
CHROME = os.environ.get("GAZETTE_CHROME") or (_cloud if Path(_cloud).exists() else None)
INK, SOFT, BLOOD = "#241a0f", "#55432b", "#7b2416"
PAPER, DEEP, RULE = "#e8dab8", "#d9c79d", "#3b2b18"
FONTS = ("https://fonts.googleapis.com/css2?family=Alfa+Slab+One&family=IM+Fell+English+SC"
         "&family=UnifrakturMaguntia&display=swap")
W = 560  # largeur utile en px

ep_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "episodes" / "s01e01.json"
ep = json.loads(ep_path.read_text(encoding="utf-8"))
slug = f"s{ep['season']:02d}e{ep['episode']:02d}"
code = f"S{ep['season']:02d}EP{ep['episode']:02d}"
assets = ROOT / "dist" / "email-assets"
assets.mkdir(parents=True, exist_ok=True)
src_url = {s["id"]: s["url"] for s in ep["sources"]}
src_num = {s["id"]: i + 1 for i, s in enumerate(ep["sources"])}

CREST = ('<svg width="64" height="64" viewBox="0 0 80 80"><path d="M40 4 L70 14 L70 40 Q70 64 40 76 Q10 64 10 40 L10 14Z" '
         'fill="none" stroke="#241a0f" stroke-width="2.5"/><path d="M40 10 L64 18 L64 40 Q64 59 40 70 Q16 59 16 40 L16 18Z" '
         'fill="none" stroke="#241a0f" stroke-width="1"/><text x="40" y="50" text-anchor="middle" '
         'font-family="UnifrakturMaguntia" font-size="30" fill="#241a0f">GC</text></svg>')


def nb(s):  # espaces insécables à la française
    return re.sub(r" ([:?!;»])", " \\1", s).replace("« ", "« ")


def md(s):
    spans = []
    s = html.escape(nb(s), quote=False)
    s = re.sub(r"`([^`]+)`", lambda m: spans.append(m.group(1)) or f"\0{len(spans) - 1}\0", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[\^([\w-]+)\]", lambda m: (
        f'<sup style="font-size:10px;line-height:0"><a href="{src_url[m.group(1)]}" style="color:{BLOOD};text-decoration:none">'
        f'[{src_num[m.group(1)]}]</a></sup>') if m.group(1) in src_url else "", s)
    s = re.sub(r"\[([^\]]+)\]\((https://[^)\s]+)\)", rf'<a href="\2" style="color:{BLOOD}">\1</a>', s)
    return re.sub(r"\0(\d+)\0", lambda m: (
        f'<code style="font-family:\'Courier New\',monospace;font-size:13px;background:#d9c79d;padding:0 3px;overflow-wrap:anywhere;word-break:break-word">'
        f'{spans[int(m.group(1))]}</code>'), s)


def datauri(data, mime):
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


# ---------------------------------------------------------------- images
def render_images(pw):
    browser = pw.chromium.launch(executable_path=CHROME)
    ctx = browser.new_context(viewport={"width": 800, "height": 600}, device_scale_factor=2)
    page = ctx.new_page()
    out = {}

    def text_png(key, text, family, size, align="center", upper=False, spacing="0", lh="1", width=W):
        html_doc = f"""<html><head><link rel="stylesheet" href="{FONTS}"></head><body style="margin:0;background:transparent">
        <div id="t" style="width:{width}px;font-family:'{family}';font-size:{size}px;line-height:{lh};color:{INK};
        padding:8px 0 2px;text-align:{align};letter-spacing:{spacing};{'text-transform:uppercase;' if upper else ''}text-wrap:balance">{html.escape(nb(text))}</div></body></html>"""
        page.set_content(html_doc)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(400)
        data = page.locator("#t").screenshot(omit_background=True)
        (assets / f"{key}.png").write_bytes(data)
        out[key] = (data, "image/png")

    # bandeau : blason, titre en gothique, filet et sous-titre
    page.set_content(f"""<html><head><link rel="stylesheet" href="{FONTS}"></head><body style="margin:0;background:transparent">
      <div id="t" style="width:{W}px"><div style="display:flex;align-items:center;justify-content:space-between">
      {CREST}<div style="font-family:'UnifrakturMaguntia';font-size:50px;line-height:1;color:{INK}">{html.escape(ep['series'])}</div>{CREST}</div>
      <div style="margin-top:8px;border-block:1px solid {RULE};padding:3px 0;text-align:center;font-family:'IM Fell English SC';
      letter-spacing:.14em;font-size:11px;text-transform:uppercase;color:{INK}">{html.escape(ep['tagline'])}</div></div></body></html>""")
    page.evaluate("document.fonts.ready"); page.wait_for_timeout(500)
    data = page.locator("#t").screenshot(omit_background=True)
    (assets / "masthead.png").write_bytes(data); out["masthead"] = (data, "image/png")

    text_png("h-brief", "En bref", "Alfa Slab One", 22, upper=True, spacing=".08em", width=200)
    text_png("h-main", ep["headline"]["title"], "Alfa Slab One", 44, upper=True, lh=".98")
    if ep.get("sideStory"):
        text_png("h-side", ep["sideStory"]["title"], "Alfa Slab One", 26, align="left", upper=True, lh="1")
    for a in ep["articles"]:
        text_png(f"h-{a['id']}", a["title"], "Alfa Slab One", 26, align="left", upper=True, lh="1")
    browser.close()
    return out


def render_scene_media(pw, page_html):
    """GIF animé de la scène « contexte » et PNG des autres scènes, pris sur la vraie page."""
    browser = pw.chromium.launch(executable_path=CHROME)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.set_content(f'<!doctype html><html><head><meta charset="utf-8"></head><body style="margin:0">{page_html}</body></html>')
    page.wait_for_timeout(2500)
    res = {}

    def freeze(css):
        page.evaluate("""css => { let s = document.getElementById('freeze'); if (!s) { s = document.createElement('style'); s.id = 'freeze'; document.head.appendChild(s); } s.textContent = css; }""", css)

    base = ".plate::after,.plate::before{animation:none!important}.term-line{animation:none!important;opacity:1!important}.cursor{animation:none!important}"
    hero = page.locator(".hero .plate")
    is_ctx = page.locator(".hero .ctx-fill").count() > 0
    if is_ctx:
        frames, n = [], 30
        for i in range(n):
            t = i * 12 / n
            freeze(base + f".ctx-fill,.ctx-sum,.ctx-sumlbl,.ctx-flash{{animation-delay:-{t:.2f}s!important;animation-play-state:paused!important}}")
            frames.append(Image.open(io.BytesIO(hero.screenshot())).convert("RGB").resize((W, int(W * 0.75)), Image.LANCZOS))
        buf = io.BytesIO()
        pal = frames[0].quantize(colors=48, method=Image.Quantize.MEDIANCUT)
        qf = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
        qf[0].save(buf, format="GIF", save_all=True, append_images=qf[1:], duration=400, loop=0, optimize=True, disposal=1)
        res["hero"] = (buf.getvalue(), "image/gif")
        (assets / "hero.gif").write_bytes(buf.getvalue())
    else:
        freeze(base)
        data = hero.screenshot(); res["hero"] = (data, "image/png"); (assets / "hero.png").write_bytes(data)
    freeze(base)
    for a in ep["articles"]:
        loc = page.locator(f"#{a['id']} .plate")
        if loc.count():
            data = loc.first.screenshot()
            im = Image.open(io.BytesIO(data)).convert("RGB"); im = im.resize((W, int(W * im.height / im.width)), Image.LANCZOS)
            b = io.BytesIO(); im.save(b, format="PNG", optimize=True)
            res[a["id"]] = (b.getvalue(), "image/png"); (assets / f"m-{a['id']}.png").write_bytes(b.getvalue())
    browser.close()
    return res


# ---------------------------------------------------------------- e-mail
def img(imgs, key, alt, width=W, align=None):
    data, mime = imgs[key]
    im = Image.open(io.BytesIO(data))
    h = round(width * im.height / im.width)
    a = f' align="{align}"' if align else ""
    return (f'<img src="{datauri(data, mime)}" alt="{html.escape(alt)}" width="{width}" height="{h}"{a} '
            f'style="display:block;width:100%;max-width:{width}px;height:auto;border:0">')


def p(s, size=15):
    return (f'<p style="margin:0 0 10px;font-family:Georgia,\'Times New Roman\',serif;font-size:{size}px;line-height:1.55;'
            f'color:{INK}">{md(s)}</p>')


def kicker(t):
    return (f'<div style="font-family:Georgia,serif;font-variant:small-caps;letter-spacing:.12em;font-size:12px;'
            f'color:{BLOOD};text-transform:lowercase;padding-top:4px">{html.escape(t)}</div>')


def rule(px=1):
    return f'<tr><td style="padding:14px 0"><div style="border-top:{px}px solid {RULE};font-size:0;line-height:0">&nbsp;</div></td></tr>'


def codebox(c):
    return (f'<table width="100%" cellpadding="0" cellspacing="0" style="margin:6px 0 10px;border:1px solid {RULE}"><tr>'
            f'<td style="background:#d9c79d;padding:4px 8px;font-family:Georgia,serif;font-size:11px;color:{INK};border-bottom:1px solid {RULE}">{html.escape(c["label"])}</td></tr>'
            f'<tr><td style="background:{INK};padding:8px 10px"><pre style="margin:0;font-family:\'Courier New\',monospace;font-size:12px;'
            f'line-height:1.4;color:{PAPER};white-space:pre-wrap">{html.escape(c["text"])}</pre></td></tr></table>')


def build_email(imgs, media):
    rows = []
    add = rows.append
    add(f'<tr><td>{img(imgs, "masthead", ep["series"])}</td></tr>')
    add(f'''<tr><td style="padding-top:12px"><table width="100%" cellpadding="0" cellspacing="0" style="border:3px double {RULE}"><tr>
      <td align="center" style="padding:8px">
      <div style="font-family:Georgia,serif;font-weight:bold;font-size:22px;letter-spacing:.04em;color:{INK}">{code}</div>
      <div style="font-family:Georgia,serif;font-style:italic;font-size:15px;line-height:1.3;color:{INK};padding:2px 0">{html.escape(nb(ep["theme"]))}</div>
      <div style="font-family:Georgia,serif;font-variant:small-caps;letter-spacing:.08em;font-size:13px;color:{SOFT}">{html.escape(ep["dateLabel"])}</div>
      </td></tr></table></td></tr>''')
    # En bref
    items = ep["brief"]["items"]
    cells = []
    for i in items:
        # Bloc entier cliquable : lien d'ancre vers la rubrique (Gmail sur ordinateur ; ignoré ailleurs)
        txt = re.sub(r"</?a\b[^>]*>", "", md(i["text"]))
        cells.append(f'''<td width="50%" valign="top" style="padding:3px"><a href="#{i.get("anchor", "une")}" style="display:block;text-decoration:none;color:{INK}"><table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {RULE};background:#dfcfa6"><tr>
          <td style="padding:7px 9px"><div style="font-family:Georgia,'Times New Roman',serif;font-weight:bold;font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:{INK}">{html.escape(i["label"])} <span style="color:{BLOOD}">&#8595;</span></div>
          <div style="font-family:Georgia,serif;font-size:13px;line-height:1.4;color:{INK};padding-top:2px">{txt}</div></td></tr></table></a></td>''')
    grid = "".join(f"<tr>{cells[k]}{cells[k + 1] if k + 1 < len(cells) else '<td></td>'}</tr>" for k in range(0, len(cells), 2))
    add(f'''<tr><td style="padding-top:14px"><table width="100%" cellpadding="0" cellspacing="0" style="border:3px double {RULE}"><tr><td style="padding:8px 8px 6px">
      <div style="padding:0 0 6px;border-bottom:1px solid {RULE};margin-bottom:6px;text-align:center">{img(imgs, "h-brief", "En bref", 200).replace("display:block", "display:inline-block")}</div>
      <table width="100%" cellpadding="0" cellspacing="0">{grid}</table></td></tr></table></td></tr>''')
    # titre à la une
    h = ep["headline"]
    add(f'<tr><td style="padding-top:16px;border-top:4px solid {RULE}"><a name="une" id="une"></a><div style="margin-top:12px">{img(imgs, "h-main", h["title"])}</div>'
        f'<div style="font-family:Georgia,serif;font-style:italic;font-size:17px;line-height:1.35;text-align:center;color:{INK};padding:8px 12px 0">{html.escape(nb(h["deck"]))}</div></td></tr>')
    add(f'<tr><td style="padding-top:14px">{img(media, "hero", h["media"].get("caption", ""))}'
        f'<div style="font-family:Georgia,serif;font-style:italic;font-size:12px;text-align:center;color:{SOFT};padding:5px 0 10px">{html.escape(nb(h["media"].get("caption", "")))}</div>'
        + "".join(p(x) for x in h["body"]) + f'<div style="font-family:Georgia,serif;font-variant:small-caps;font-size:12px;color:{SOFT}">{html.escape(h.get("byline", ""))}</div></td></tr>')
    if ep.get("sideStory"):
        s = ep["sideStory"]
        add(rule(1))
        add(f'<tr><td>{kicker(s["kicker"])}<div style="padding:4px 0 8px">{img(imgs, "h-side", s["title"])}</div>' + "".join(p(x) for x in s["body"]) + "</td></tr>")
    for a in ep["articles"]:
        add(rule(1))
        m = ""
        if a["id"] in media:
            m = f'<div style="padding:0 0 8px">{img(media, a["id"], a.get("media", {}).get("caption", a["title"]))}</div>'
        add(f'<tr><td><a name="{a["id"]}" id="{a["id"]}"></a>{kicker(a["kicker"])}<div style="padding:4px 0 8px">{img(imgs, "h-" + a["id"], a["title"])}</div>{m}'
            + "".join(p(x) for x in a["body"]) + (codebox(a["code"]) if a.get("code") else "") + "</td></tr>")
    add(rule(3))
    srcs = "".join(f'<div style="font-family:Georgia,serif;font-size:12px;line-height:1.4;color:{INK};padding:1px 0">[{i + 1}] '
                   f'<a href="{s["url"]}" style="color:{BLOOD}">{html.escape(s["title"])}</a> · <span style="color:{SOFT}">{html.escape(s["publisher"])}</span></div>'
                   for i, s in enumerate(ep["sources"]))
    add(f'<tr><td><div style="font-family:Georgia,serif;font-variant:small-caps;letter-spacing:.16em;font-size:13px;text-align:center;padding-bottom:6px">Sources citées</div>{srcs}'
        f'<div style="font-family:\'Courier New\',monospace;font-size:11px;text-align:center;color:{SOFT};padding-top:12px">{html.escape(ep["series"])} · {code} · {ep["date"]}</div></td></tr>')
    body = "\n".join(rows)
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(ep["series"])} {code} (e-mail)</title></head>
<body style="margin:0;background:{DEEP}">
<table width="100%" cellpadding="0" cellspacing="0" bgcolor="{DEEP}" style="background:{DEEP}"><tr><td align="center" style="padding:16px 8px">
<table width="{W + 44}" cellpadding="0" cellspacing="0" bgcolor="{PAPER}" style="width:100%;max-width:{W + 44}px;background:{PAPER};border:3px double {RULE}"><tr><td style="padding:20px 22px">
<table width="100%" cellpadding="0" cellspacing="0">
{body}
</table></td></tr></table></td></tr></table></body></html>'''


# ---------------------------------------------------------------- Google Chat
def chat_text(url):
    def conv(s):
        s = re.sub(r"\[\^[\w-]+\]", "", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", s)
        s = re.sub(r"\[([^\]]+)\]\((https://[^)\s]+)\)", r"<\2|\1>", s)
        return nb(s)
    lines = [f"*{ep['series']} · {code}*", f"_{conv(ep['theme'])}_", "", "*En bref*"]
    lines += [f"• *{i['label']}* : {conv(i['text'])}" for i in ep["brief"]["items"]]
    lines += ["", f"Le numéro complet : {url}"]
    return "\n".join(lines)


def main():
    page_html = (ROOT / "dist" / f"{slug}.html").read_text(encoding="utf-8")
    with sync_playwright() as pw:
        imgs = render_images(pw)
        media = render_scene_media(pw, page_html)
    out = ROOT / "dist" / f"{slug}-email.html"
    out.write_text(build_email(imgs, media), encoding="utf-8")
    url = ep.get("publicUrl", "[lien de la page]")
    (ROOT / "dist" / f"{slug}-chat.txt").write_text(chat_text(url), encoding="utf-8")
    print(out, f"{out.stat().st_size // 1024} Ko")


if __name__ == "__main__":
    main()
