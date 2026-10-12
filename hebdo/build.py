#!/usr/bin/env python3
"""Construit le site de La Gazette de l'Algorithme à partir des numéros.

    python3 hebdo/build.py            ->  hebdo/_site/ (site statique complet)
    python3 hebdo/build.py --check    ->  valide les numéros sans rien écrire
    python3 hebdo/build.py --brouillon -> hebdo/_brouillon/ : aperçu local qui inclut les brouillons

Un numéro = un fichier hebdo/numeros/AAAA-MM-JJ.json (date de parution, un lundi).
Le plus récent fait la une de index.html ; tous sont dans /numero/<date>/ et /archives/.
Aucune dépendance : bibliothèque standard Python uniquement.
"""
import html
import json
import re
import shutil
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
OUT = ROOT / "_site"
BRAND = json.loads((REPO / "config" / "brand.json").read_text(encoding="utf-8"))
SITE_URL = BRAND.get("siteUrl", "").rstrip("/")

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


# ---------- dates ----------

def d(s):
    return date.fromisoformat(s)


def date_longue(s, jour=True):
    x = d(s)
    j = f"{JOURS[x.weekday()].capitalize()} " if jour else ""
    return f"{j}{x.day}{'er' if x.day == 1 else ''} {MOIS[x.month - 1]} {x.year}"


def periode(p):
    a, b = d(p["du"]), d(p["au"])
    if a.month == b.month:
        return f"Semaine du {a.day} au {b.day} {MOIS[b.month - 1]} {b.year}"
    return f"Semaine du {a.day} {MOIS[a.month - 1]} au {b.day} {MOIS[b.month - 1]} {b.year}"


# ---------- texte ----------

def fr(s):
    """Typographie française : espaces insécables fines avant ; ! ? et insécables avant : et dans « »."""
    s = re.sub(r" ([;!?])", " \\1", s)
    s = re.sub(r" (:)(?!//)", " \\1", s)
    s = s.replace("« ", "« ").replace(" »", " »")
    return re.sub(r"(?<=\w)'(?=\w)", "’", s)


class Ctx:
    """Numérotation des sources dans l'ordre de première citation."""

    def __init__(self, sources):
        self.by_id = {s["id"]: s for s in sources}
        self.order = []
        self.vues = {}

    def appel(self, sid):
        """Numéro de la source et identifiant unique de cet appel (pour le lien retour)."""
        n = self.num(sid)
        self.vues[sid] = self.vues.get(sid, 0) + 1
        return n, f"cite-{n}-{self.vues[sid]}"

    def num(self, sid):
        if sid not in self.order:
            self.order.append(sid)
        return self.order.index(sid) + 1


def md(s, ctx):
    """Balisage minimal : `code`, **gras**, *italique*, [texte](https://…), [^idSource]."""
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", keep, s)
    s = fr(html.escape(s, quote=False))
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" rel="noopener">\1</a>', s)

    def cite(m):
        n, ident = ctx.appel(m.group(1))
        src = ctx.by_id[m.group(1)]
        t = html.escape(f"{src.get('editeur', '')} : {src['titre']}", quote=True)
        return f'<sup class="ref"><a id="{ident}" href="#source-{n}" title="{t}" aria-label="Source {n} : {t}">{n}</a></sup>'

    s = re.sub(r"\[\^([\w-]+)\]", cite, s)
    s = s.replace('</a></sup><sup class="ref"><a', '</a>,\u2009<a')
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{html.escape(codes[int(m.group(1))])}</code>", s)


def e(s):
    return html.escape(fr(str(s)), quote=True)


# ---------- validation ----------

def valider(n, path):
    err = []
    for k in ("numero", "date", "periode", "resume", "une", "articles", "sources"):
        if k not in n:
            err.append(f"champ manquant : {k}")
    if err:
        return err
    if d(n["date"]).weekday() != 0:
        err.append("la date de parution doit être un lundi")
    if path.stem != n["date"]:
        err.append(f"le fichier doit s'appeler {n['date']}.json")
    if n.get("statut", "publie") not in ("brouillon", "publie"):
        err.append("statut doit valoir « brouillon » ou « publie »")
    if not all(isinstance(x, str) for x in n.get("relecture", [])):
        err.append("relecture doit être une liste de phrases")
    blob = json.dumps({k: v for k, v in n.items() if k != "relecture"}, ensure_ascii=False)
    if "—" in blob or "–" in blob:
        err.append("tirets cadratin ou demi-cadratin interdits : utiliser une virgule, deux-points ou un trait d'union")
    ids = [s["id"] for s in n["sources"]]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        err.append(f"sources en double : {', '.join(sorted(dup))}")
    for s in n["sources"]:
        for k in ("id", "titre", "url"):
            if not s.get(k):
                err.append(f"source {s.get('id', '?')} : champ {k} manquant")
    cites = set(re.findall(r"\[\^([\w-]+)\]", blob))
    manquantes = cites - set(ids)
    if manquantes:
        err.append(f"citations sans source : {', '.join(sorted(manquantes))}")
    inutiles = set(ids) - cites
    if inutiles:
        err.append(f"sources jamais citées : {', '.join(sorted(inutiles))}")
    for bloc in [n["une"], *n["articles"]]:
        if not bloc.get("titre") or not bloc.get("corps"):
            err.append(f"article sans titre ou sans corps : {bloc.get('id', '?')}")
        elif not re.search(r"\[\^", json.dumps(bloc, ensure_ascii=False)):
            err.append(f"article sans aucune citation : {bloc.get('id', '?')}")
    for b in n.get("breves", []):
        if "[^" not in b.get("texte", ""):
            err.append(f"brève sans citation : {b.get('titre', '?')}")
    return err


def charger():
    numeros, erreurs = [], []
    for p in sorted((ROOT / "numeros").glob("*.json")):
        try:
            n = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as x:
            erreurs.append(f"{p.name} : JSON invalide ({x})")
            continue
        for m in valider(n, p):
            erreurs.append(f"{p.name} : {m}")
        n["_path"] = p
        numeros.append(n)
    numeros.sort(key=lambda n: n["date"], reverse=True)
    return numeros, erreurs


# ---------- fragments ----------

def figure(f, ctx, cls=""):
    if not f:
        return ""
    t = f.get("type")
    leg = f'<figcaption>{md(f["legende"], ctx)}</figcaption>' if f.get("legende") else ""
    if t == "chiffre":
        label = e(f"{f['valeur']} {f.get('unite', '')} : " + re.sub(r"\[\^[\w-]+\]|[*`]", "", f.get("legende", "")))
        return f"""<figure class="plaque {cls}">
  <div class="plaque-cadre" role="img" aria-label="{label}">
    <div class="plaque-gravure" aria-hidden="true"></div>
    <div class="plaque-lueur" aria-hidden="true"></div>
    <p class="plaque-valeur" aria-hidden="true">{e(f['valeur'])}</p>
    <p class="plaque-unite" aria-hidden="true">{e(f.get('unite', ''))}</p>
  </div>{leg}
</figure>"""
    if t == "citation":
        return f"""<figure class="exergue {cls}">
  <blockquote><p>{md(f['texte'], ctx)}</p></blockquote>
  <figcaption>{md(f['auteur'], ctx)}</figcaption>
</figure>"""
    if t == "image":
        return f"""<figure class="cliche {cls}">
  <img src="{{base}}{e(f['src'])}" alt="{e(f.get('alt', ''))}" loading="lazy" decoding="async">{leg}
</figure>"""
    sys.exit(f"Type de figure inconnu : {t}")


def corps(paras, ctx):
    return "".join(f"<p>{md(p, ctx)}</p>" for p in paras)


def article(a, ctx, forme):
    fig = figure(a.get("figure"), ctx, "article-figure")
    chapo = f'<p class="chapo">{md(a["chapo"], ctx)}</p>' if a.get("chapo") else ""
    return f"""<article class="papier papier--{forme}" id="{e(a['id'])}" aria-labelledby="{e(a['id'])}-t">
  <h3 class="papier-titre" id="{e(a['id'])}-t">{md(a['titre'], ctx)}</h3>
  {chapo}
  <div class="papier-corps">{corps(a['corps'], ctx)}</div>
  {fig}
</article>"""


FORMES = ["large", "etroit", "etroit", "large", "plein"]


def numero_html(n, base, est_une, prec=None, suiv=None):
    ctx = Ctx(n["sources"])
    u = n["une"]
    sommaire = [(u.get("id", "une"), u.get("titreCourt", u["titre"]))]
    sommaire += [(a["id"], a.get("titreCourt", a["titre"])) for a in n["articles"]]
    if n.get("breves"):
        sommaire.append(("hiboux", "Hiboux express"))
    if n.get("salleCommune"):
        sommaire.append(("salle-commune", "La salle commune"))
    som = "".join(f'<li><a href="#{e(i)}">{md(t, Ctx([]))}</a></li>' for i, t in sommaire)

    une = f"""<section class="une" id="{e(u.get('id', 'une'))}" aria-labelledby="une-t">
  <h2 class="filet-titre"><span>À la une</span></h2>
  <div class="une-grille">
    <div class="une-texte">
      <h2 class="une-titre" id="une-t">{md(u['titre'], ctx)}</h2>
      <p class="une-chapo">{md(u['chapo'], ctx)}</p>
      <div class="une-corps lettrine">{corps(u['corps'], ctx)}</div>
    </div>
    <aside class="une-aside">{figure(u.get('figure'), ctx, 'une-figure')}</aside>
  </div>
</section>"""

    arts = "".join(article(a, ctx, FORMES[i % len(FORMES)] if not (i == len(n["articles"]) - 1 and i % 2 == 0) else "plein")
                   for i, a in enumerate(n["articles"]))

    breves = ""
    if n.get("breves"):
        items = "".join(f"<li><h3>{md(b['titre'], ctx)}</h3><p>{md(b['texte'], ctx)}</p></li>" for b in n["breves"])
        breves = f"""<section class="hiboux" id="hiboux" aria-labelledby="hiboux-t">
  <h2 class="filet-titre" id="hiboux-t"><span>Hiboux express</span></h2>
  <ul class="hiboux-liste">{items}</ul>
</section>"""

    salle = ""
    sc = n.get("salleCommune")
    if sc:
        rows = []
        # Le lieu n'est imprimé que s'il varie d'un fil à l'autre.
        un_lieu = len({it.get("lieu") for it in sc["items"]}) == 1
        for it in sc["items"]:
            chiffres = []
            if it.get("points") is not None:
                chiffres.append(f'<span><strong>{int(it["points"]):,}</strong> points</span>'.replace(",", " "))
            if it.get("commentaires") is not None:
                chiffres.append(f'<span><strong>{int(it["commentaires"]):,}</strong> commentaires</span>'.replace(",", " "))
            note = f'<p class="salle-note">{md(it["note"], ctx)}</p>' if it.get("note") else ""
            rows.append(f"""<li>
  {'' if un_lieu else f'<p class="salle-lieu">{e(it["lieu"])}</p>'}
  <h3 class="salle-titre"><a href="{e(it['url'])}" rel="noopener">{e(it['titre'])}</a></h3>
  <p class="salle-chiffres">{''.join(chiffres)}</p>{note}
</li>""")
        intro = f'<p class="salle-intro">{md(sc["intro"], ctx)}</p>' if sc.get("intro") else ""
        salle = f"""<section class="salle" id="salle-commune" aria-labelledby="salle-t">
  <h2 class="filet-titre" id="salle-t"><span>La salle commune</span></h2>
  {intro}
  <ol class="salle-liste">{''.join(rows)}</ol>
</section>"""

    # Sources : rendues en dernier, dans l'ordre de citation.
    src_items = []
    for i, sid in enumerate(ctx.order, 1):
        s = ctx.by_id[sid]
        meta = ", ".join(x for x in (s.get("editeur"), date_longue(s["date"], False) if s.get("date") else None) if x)
        src_items.append(f'<li id="source-{i}"><a href="{e(s["url"])}" rel="noopener">{e(s["titre"])}</a>'
                         f'{f" <span>{e(meta)}</span>" if meta else ""}'
                         f' <a class="retour" href="#cite-{i}-1" aria-label="Retour au texte, source {i}">retour au texte</a></li>')
    sources = f"""<section class="sources" aria-labelledby="sources-t">
  <h2 class="filet-titre" id="sources-t"><span>Sources</span></h2>
  <ol>{''.join(src_items)}</ol>
</section>"""

    lien = "" if not est_une else f'<a href="{base}numero/{n["date"]}/">Lien permanent</a>'
    nav = []
    if prec:
        nav.append(f'<a rel="prev" href="{base}numero/{prec["date"]}/">← N° {prec["numero"]}, {e(date_longue(prec["date"], False))}</a>')
    if suiv:
        nav.append(f'<a rel="next" href="{base}numero/{suiv["date"]}/">N° {suiv["numero"]}, {e(date_longue(suiv["date"], False))} →</a>')
    elif n.get("statut", "publie") == "publie":
        prochain = (d(n["date"]) + timedelta(days=7)).isoformat()
        nav.append(f'<span>Prochain numéro {e(date_longue(prochain).lower())}. <a href="{base}feed.xml">Flux RSS</a></span>')
    numeros_nav = f'<nav class="numeros-nav" aria-label="Autres numéros">{"".join(nav)}</nav>' if nav else ""
    resume = f'<p class="numero-resume">{md(n["resume"], Ctx([]))}</p>' if n.get("resume") else ""
    relecture = ""
    if n.get("statut") == "brouillon":
        points = "".join(f"<li>{md(x, Ctx([]))}</li>" for x in n.get("relecture", [])) or "<li>Aucun point signalé par la rédaction.</li>"
        relecture = f"""<aside class="relecture" aria-labelledby="relecture-t">
  <h2 id="relecture-t">Brouillon à relire</h2>
  <p>Ce numéro n'est pas publié. Points que la rédaction n'a pas pu confirmer ou qu'elle te demande de trancher :</p>
  <ul>{points}</ul>
  <p class="relecture-cmd">Corriger : <code>make gazette-corriger M="…"</code>. Publier tel quel : <code>make gazette-publier</code>.</p>
</aside>"""
    return f"""<main id="contenu" class="journal">
{relecture}
{resume}
<nav class="sommaire" aria-label="Dans ce numéro"><p>Dans ce numéro</p><ol>{som}</ol></nav>
{une}
<div class="papiers">{arts}</div>
{breves}
{salle}
{sources}
<p class="numero-pied">N° {n['numero']}, {e(date_longue(n['date']).lower())}. {lien}</p>
{numeros_nav}
</main>"""


def page(titre, description, base, contenu, n=None, canon="", corps_cls=""):
    edition = ""
    if n:
        edition = f"""<div class="bandeau">
  <p class="bandeau-num">N° {n['numero']}</p>
  <p class="bandeau-devise">{e(BRAND.get('tagline', ''))}</p>
  <p class="bandeau-date"><time datetime="{n['date']}">{e(date_longue(n['date']))}</time><br><span>{e(periode(n['periode']))}</span></p>
</div>"""
    else:
        edition = f"""<div class="bandeau bandeau--simple"><p class="bandeau-devise">{e(BRAND.get('tagline', ''))}</p></div>"""
    can = f'<link rel="canonical" href="{SITE_URL}/{canon}">' if SITE_URL else ""
    og_url = f'<meta property="og:url" content="{SITE_URL}/{canon}">' if SITE_URL else ""
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre)}</title>
<meta name="description" content="{e(description)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{e(titre)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:locale" content="fr_FR">{og_url}
{can}
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#ece2c9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#16140f" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{e(BRAND['name'])}" href="{base}feed.xml">
<link rel="preload" href="{base}assets/fonts/unifrakturmaguntia-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{base}assets/fonts/playfair-display-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{base}assets/fonts/source-serif-4-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}assets/gazette.css">
<script>try{{var t=localStorage.getItem("gazette-theme");if(t)document.documentElement.dataset.theme=t}}catch(_){{}}</script>
</head>
<body class="{corps_cls}">
<a class="evitement" href="#contenu">Aller au contenu</a>
<header class="tete">
  <nav class="outils" aria-label="Navigation">
    <a href="{base}"{' aria-current="page"' if "page-une" in corps_cls else ''}>Dernier numéro</a>
    <a href="{base}archives/"{' aria-current="page"' if "page-archives" in corps_cls else ''}>Archives</a>
    <a href="{base}feed.xml">RSS</a>
    <button type="button" class="theme" data-theme-toggle aria-pressed="false" aria-label="Mode nuit (Nox)" hidden>
      <span class="theme-nuit">Nox</span><span class="theme-jour">Lumos</span>
    </button>
  </nav>
  {'<h1 class="titre-h1">' if n else ''}<a class="titre-journal" href="{base}" aria-label="{e(BRAND['name'])}, accueil">
    <span class="titre-encre">{e(BRAND['name'])}</span>
  </a>{'</h1>' if n else ''}
  {edition}
</header>
{contenu}
<footer class="pied">
  <p>{e(BRAND['name'])} paraît chaque lundi. Chaque fait renvoie à sa source ; rien n'est affirmé sans elle.</p>
  <p><a href="{base}archives/">Tous les numéros</a> <a href="{base}feed.xml">Flux RSS</a></p>
</footer>
<script src="{base}assets/gazette.js" defer></script>
</body>
</html>
"""


def archives_html(numeros, base):
    if not numeros:
        return '<main id="contenu" class="archives"><h1>Archives</h1><p class="vide">Aucun numéro pour l\'instant. Le premier paraîtra lundi.</p></main>'
    groupes = {}
    for n in numeros:
        x = d(n["date"])
        groupes.setdefault((x.year, x.month), []).append(n)
    blocs = []
    for (y, m), ns in groupes.items():
        lis = "".join(f"""<li>
  <a href="{base}numero/{n['date']}/">
    <span class="arch-num">N° {n['numero']}</span>
    <span class="arch-titre">{md(n['une']['titre'], Ctx(n['sources']))}</span>
    <span class="arch-resume">{e(n['resume'])}</span>
    <time datetime="{n['date']}">{e(date_longue(n['date']))}</time>
  </a>
</li>""" for n in ns)
        blocs.append(f'<section><h2>{MOIS[m - 1].capitalize()} {y}</h2><ol>{lis}</ol></section>')
    return f"""<main id="contenu" class="archives">
<h1>Archives</h1>
<p class="archives-intro">{len(numeros)} numéro{'s' if len(numeros) > 1 else ''} depuis le {e(date_longue(numeros[-1]['date'], False))}.</p>
{''.join(blocs)}
</main>"""


def rss(numeros):
    items = []
    for n in numeros[:30]:
        link = f"{SITE_URL}/numero/{n['date']}/" if SITE_URL else f"numero/{n['date']}/"
        pub = datetime.combine(d(n["date"]), datetime.min.time(), timezone.utc).strftime("%a, %d %b %Y 07:00:00 +0000")
        titre = re.sub(r"\[\^[\w-]+\]|[*`]", "", n["une"]["titre"])
        items.append(f"""<item><title>{html.escape(f"N° {n['numero']} : {titre}")}</title><link>{html.escape(link)}</link>
<guid isPermaLink="false">gazette-{n['date']}</guid><pubDate>{pub}</pubDate><description>{html.escape(n['resume'])}</description></item>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel>
<title>{html.escape(BRAND['name'])}</title><link>{html.escape(SITE_URL or '.')}/</link>
<description>{html.escape(BRAND.get('tagline', ''))}</description><language>fr</language>
{''.join(items)}
</channel></rss>
"""


def voisins(numeros, i):
    """(numéro précédent, numéro suivant) ; la liste va du plus récent au plus ancien."""
    return (numeros[i + 1] if i + 1 < len(numeros) else None, numeros[i - 1] if i > 0 else None)


def cls(n):
    return "est-brouillon" if n.get("statut") == "brouillon" else ""


def ecrire(path, texte):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(texte, encoding="utf-8")


def main():
    global OUT
    numeros, erreurs = charger()
    if erreurs:
        print("Numéros invalides :\n  " + "\n  ".join(erreurs), file=sys.stderr)
        sys.exit(1)
    if "--check" in sys.argv:
        print(f"{len(numeros)} numéro(s) valides.")
        return
    brouillon = "--brouillon" in sys.argv
    if brouillon:
        # Aperçu local : les brouillons sont inclus et signalés. Jamais déployé.
        OUT = ROOT / "_brouillon"
    else:
        numeros = [n for n in numeros if n.get("statut", "publie") == "publie"]
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    nom = BRAND["name"]
    for i, n in enumerate(numeros):
        titre_une = re.sub(r"\[\^[\w-]+\]|[*`]", "", n["une"]["titre"])
        t = f"{'[Brouillon] ' if n.get('statut') == 'brouillon' else ''}{titre_une} | {nom}, n° {n['numero']}"
        ecrire(OUT / "numero" / n["date"] / "index.html",
               page(t, n["resume"], "../../", numero_html(n, "../../", False, *voisins(numeros, i)), n, f"numero/{n['date']}/", cls(n)).replace("{base}", "../../"))
        if i == 0:
            ecrire(OUT / "index.html",
                   page(f"{nom} : {titre_une}", n["resume"], "", numero_html(n, "", True, *voisins(numeros, i)), n, f"numero/{n['date']}/", (cls(n) + " page-une").strip()).replace("{base}", ""))
    if not numeros:
        ecrire(OUT / "index.html", page(nom, BRAND.get("tagline", ""), "", archives_html([], ""), None, ""))
    ecrire(OUT / "archives" / "index.html",
           page(f"Archives | {nom}", f"Tous les numéros de {nom}.", "../", archives_html(numeros, "../"), None, "archives/", "page-archives"))
    racine = SITE_URL + "/" if SITE_URL else "./"
    ecrire(OUT / "404.html", page(f"Page introuvable | {nom}", "Page introuvable.", racine,
                                  f'<main id="contenu" class="archives"><h1>Ce parchemin a disparu</h1><p class="vide">La page demandée n\'existe pas. <a href="{racine}">Retour au dernier numéro</a>.</p></main>'))
    ecrire(OUT / "feed.xml", rss(numeros))
    ecrire(OUT / ".nojekyll", "")
    nb = sum(n.get("statut") == "brouillon" for n in numeros)
    print(f"{OUT.relative_to(REPO)}/  ({len(numeros)} numéro(s), dernier : {numeros[0]['date'] if numeros else 'aucun'}"
          f"{f', dont {nb} brouillon(s)' if nb else ''})")


if __name__ == "__main__":
    main()
