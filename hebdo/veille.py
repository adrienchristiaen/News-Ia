#!/usr/bin/env python3
"""Veille de la semaine : collecte les candidats pour le prochain numéro.

    python3 hebdo/veille.py                 ->  hebdo/veille/<lundi>.md (+ .json)
    python3 hebdo/veille.py --date 2026-10-19

Lit les flux RSS/Atom, le top de la semaine de plusieurs subreddits (avec leurs meilleurs
commentaires), les posts X des comptes suivis et les fils IA les plus votés de Hacker News
(sources.json).

Accès officiels, à mettre dans l'environnement ou dans hebdo/.env (jamais commité) :
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET   app « script » créée sur https://www.reddit.com/prefs/apps
  X_BEARER_TOKEN                           app créée sur https://console.x.com (crédits payants à l'usage)
Sans clé Reddit, la veille tente l'accès public ; sans clé X, elle saute X et le signale. Rien n'est rédigé ici : le fichier produit est une liste
de pistes classées, que le skill gazette-ia vérifie à la source avant d'écrire quoi que ce soit.
Bibliothèque standard uniquement. Une source injoignable est signalée puis ignorée.
"""
import argparse
import base64
import os
import email.utils
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UA = "GazetteAlgorithme/1.0 (veille hebdomadaire; +https://github.com/adrienchristiaen/News-Ia)"
ATOM = "{http://www.w3.org/2005/Atom}"


def get(url, timeout=20, headers=None, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def charger_env():
    f = ROOT / ".env"
    if f.exists():
        for ligne in f.read_text(encoding="utf-8").splitlines():
            if "=" in ligne and not ligne.lstrip().startswith("#"):
                k, v = ligne.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_REDDIT = {}


def reddit_api(chemin):
    """Appel Reddit : API OAuth officielle si des identifiants existent, sinon accès public."""
    cid, sec = os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET")
    if cid and sec:
        if "token" not in _REDDIT:
            auth = base64.b64encode(f"{cid}:{sec}".encode()).decode()
            tok = json.loads(get("https://www.reddit.com/api/v1/access_token", headers={"Authorization": f"Basic {auth}"},
                                 data=b"grant_type=client_credentials"))
            _REDDIT["token"] = tok["access_token"]
        return json.loads(get("https://oauth.reddit.com" + chemin, headers={"Authorization": f"Bearer {_REDDIT['token']}"}))
    base, _, q = chemin.partition("?")
    return json.loads(get(f"https://www.reddit.com{base}.json?{q}"))


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def texte(el, *noms):
    for n in noms:
        x = el.find(n)
        if x is not None and (x.text or "").strip():
            return x.text.strip()
    return ""


def flux(src, depuis):
    out = []
    root = ET.fromstring(get(src["url"]))
    items = root.findall(".//item") or root.findall(f".//{ATOM}entry")
    for it in items:
        titre = texte(it, "title", f"{ATOM}title")
        lien = texte(it, "link")
        if not lien:
            l = it.find(f"{ATOM}link[@rel='alternate']")
            if l is None:
                l = it.find(f"{ATOM}link")
            lien = l.get("href", "") if l is not None else ""
        quand = parse_date(texte(it, "pubDate", f"{ATOM}published", f"{ATOM}updated", "{http://purl.org/dc/elements/1.1/}date"))
        resume = re.sub(r"<[^>]+>|\s+", " ", texte(it, "description", f"{ATOM}summary", f"{ATOM}content"))[:280].strip()
        if quand and quand >= depuis and titre:
            out.append({"source": src["nom"], "type": "presse", "titre": titre, "url": lien,
                        "date": quand.date().isoformat(), "resume": resume, "poids": src.get("poids", 1)})
    return out


def reddit(sub, depuis):
    data = reddit_api(f"/r/{sub}/top?t=week&limit=15&raw_json=1")
    out = []
    for c in data["data"]["children"]:
        p = c["data"]
        quand = datetime.fromtimestamp(p["created_utc"], timezone.utc)
        if quand < depuis or p.get("stickied"):
            continue
        out.append({"source": f"r/{sub}", "type": "reddit", "titre": p["title"],
                    "url": "https://www.reddit.com" + p["permalink"], "lien_externe": p.get("url_overridden_by_dest", ""),
                    "date": quand.date().isoformat(), "points": p["score"], "commentaires": p["num_comments"],
                    "resume": (p.get("selftext") or "")[:600], "poids": 1, "_permalink": p["permalink"]})
    return out


def reddit_commentaires(c, n=3):
    """Ajoute le texte des meilleurs commentaires : ce que la communauté en dit vraiment."""
    data = reddit_api(c["_permalink"].rstrip("/") + "?sort=top&limit=8&depth=1&raw_json=1")
    coms = [x["data"] for x in data[1]["data"]["children"] if x["kind"] == "t1" and not x["data"].get("stickied")]
    c["commentaires_top"] = [{"auteur": x.get("author"), "score": x.get("score"), "texte": x.get("body", "")[:500]} for x in coms[:n]]


def x_posts(cfg, depuis):
    """Posts récents des comptes suivis, via l'API officielle X v2 (recherche des 7 derniers jours)."""
    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        raise RuntimeError("X_BEARER_TOKEN absent : X ignoré (voir hebdo/README.md)")
    comptes, out, lus = cfg["comptes"], [], 0
    # Une requête par paquet de comptes (longueur de requête limitée), plafonnée par le budget.
    paquets, cur = [], []
    for c in comptes:
        if len(" OR ".join(f"from:{x}" for x in cur + [c])) > 400:
            paquets.append(cur)
            cur = []
        cur.append(c)
    if cur:
        paquets.append(cur)
    for paquet in paquets:
        if lus >= cfg.get("maxPosts", 300):
            break
        q = "(" + " OR ".join(f"from:{x}" for x in paquet) + ") -is:retweet -is:reply"
        params = urllib.parse.urlencode({
            "query": q, "max_results": min(100, cfg.get("maxPosts", 300) - lus),
            "start_time": depuis.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tweet.fields": "created_at,public_metrics,author_id,note_tweet,entities",
            "expansions": "author_id", "user.fields": "username,name"})
        data = json.loads(get(f"https://api.x.com/2/tweets/search/recent?{params}", headers={"Authorization": f"Bearer {token}"}))
        users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
        for t in data.get("data", []):
            lus += 1
            m = t.get("public_metrics", {})
            u = users.get(t["author_id"], {})
            texte = (t.get("note_tweet") or {}).get("text") or t["text"]
            engagement = m.get("like_count", 0) + 3 * m.get("retweet_count", 0) + 2 * m.get("quote_count", 0)
            if engagement < cfg.get("engagementMin", 200):
                continue
            liens = [x.get("expanded_url") for x in t.get("entities", {}).get("urls", []) if x.get("expanded_url")]
            out.append({"source": f"X @{u.get('username', '?')}", "type": "x", "titre": texte.split("\n")[0][:140],
                        "texte": texte, "url": f"https://x.com/{u.get('username', 'i')}/status/{t['id']}",
                        "lien_externe": liens[0] if liens else "", "date": t["created_at"][:10],
                        "points": m.get("like_count", 0), "commentaires": m.get("reply_count", 0), "poids": 2})
    return out


def hackernews(cfg, depuis):
    q = urllib.parse.urlencode({"query": "", "tags": "story", "hitsPerPage": 100,
                                "numericFilters": f"created_at_i>{int(depuis.timestamp())},points>{cfg['points_min']}"})
    data = json.loads(get(f"https://hn.algolia.com/api/v1/search?{q}"))
    mots = re.compile(r"\b(" + "|".join(re.escape(m.strip()) for m in cfg["requete"].split(" OR ")) + r")\b|\bIA\b|\bLLMs?\b", re.I)
    out = []
    for h in data["hits"]:
        if not mots.search(h.get("title") or ""):
            continue
        out.append({"source": "Hacker News", "type": "hn", "titre": h["title"],
                    "url": f"https://news.ycombinator.com/item?id={h['objectID']}", "lien_externe": h.get("url") or "",
                    "date": h["created_at"][:10], "points": h["points"], "commentaires": h.get("num_comments", 0), "poids": 1})
    return out


def score(c, mc):
    s = c["poids"] * 10
    t = (c["titre"] + " " + c.get("resume", "")).lower()
    s += 4 * sum(m.lower() in t for m in mc["bonus"]) - 8 * sum(m.lower() in t for m in mc["malus"])
    if c.get("points"):
        s += min(40, c["points"] / 40) + min(20, c.get("commentaires", 0) / 40)
    return round(s, 1)


def regrouper(cands):
    """Regroupe les candidats qui parlent visiblement du même sujet (mots du titre en commun)."""
    def mots(t):
        return {w for w in re.findall(r"[a-z0-9][a-z0-9.\-]{2,}", t.lower()) if w not in VIDES}
    groupes = []
    for c in sorted(cands, key=lambda c: -c["score"]):
        m = mots(c["titre"])
        for g in groupes:
            if len(m & g["mots"]) >= 3 or (len(m & g["mots"]) >= 2 and len(m) <= 5):
                g["items"].append(c)
                g["mots"] |= m
                g["score"] += c["score"] / 2
                break
        else:
            groupes.append({"mots": m, "items": [c], "score": c["score"]})
    return sorted(groupes, key=lambda g: -g["score"])


VIDES = set("the and for with from that this are was its your you how why what new now into about over after has have will can not but les des une est pour dans par sur avec qui que pas plus aux ses ces son".split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="date de parution (un lundi), par défaut le lundi qui vient ou aujourd'hui si lundi")
    args = ap.parse_args()
    today = date.today()
    lundi = date.fromisoformat(args.date) if args.date else today + timedelta(days=(7 - today.weekday()) % 7)
    charger_env()
    cfg = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    fin = datetime.combine(lundi, datetime.min.time(), timezone.utc)
    depuis = fin - timedelta(days=cfg.get("jours", 8))

    taches = [("flux " + f["nom"], flux, f) for f in cfg["flux"]]
    taches += [("reddit r/" + s, reddit, s) for s in cfg["reddit"]]
    taches.append(("Hacker News", hackernews, cfg["hackernews"]))
    if cfg.get("x"):
        taches.append(("X", x_posts, cfg["x"]))
    cands, echecs = [], []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fn, arg, depuis): nom for nom, fn, arg in taches}
        for f, nom in futs.items():
            try:
                cands += f.result()
            except Exception as x:  # une source en panne ne bloque pas la veille
                echecs.append(f"{nom} : {type(x).__name__} {str(x)[:120]}")
    cands = [c for c in cands if c["date"] < lundi.isoformat()]
    # Les meilleurs commentaires des posts Reddit les plus suivis.
    top_reddit = sorted((c for c in cands if c["type"] == "reddit"), key=lambda c: -c.get("points", 0))[:12]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for c, f in [(c, ex.submit(reddit_commentaires, c)) for c in top_reddit]:
            try:
                f.result()
            except Exception as x:
                echecs.append(f"commentaires {c['url']} : {type(x).__name__}")
    for c in cands:
        c.pop("_permalink", None)
    vus, uniques = set(), []
    for c in cands:
        k = (c.get("lien_externe") or c["url"]).split("?")[0].rstrip("/")
        if k not in vus:
            vus.add(k)
            uniques.append(c)
    for c in uniques:
        c["score"] = score(c, cfg["motsCles"])
    groupes = regrouper(uniques)

    sortie = ROOT / "veille"
    sortie.mkdir(exist_ok=True)
    (sortie / f"{lundi}.json").write_text(json.dumps({"lundi": str(lundi), "depuis": depuis.date().isoformat(),
                                                      "echecs": echecs, "groupes": [{"score": round(g["score"], 1), "items": g["items"]} for g in groupes]},
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
    lignes = [f"# Veille pour le numéro du {lundi}", "",
              f"Période : du {depuis.date()} au {lundi - timedelta(days=1)}. {len(uniques)} candidats, {len(groupes)} sujets.", ""]
    if echecs:
        lignes += ["## Sources injoignables", ""] + [f"- {e}" for e in echecs] + [""]
    lignes += ["## Sujets classés (score décroissant)", ""]
    for i, g in enumerate(groupes[:60], 1):
        lignes.append(f"### {i}. {g['items'][0]['titre']}  (score {g['score']:.0f})")
        for c in g["items"][:6]:
            extra = f", {c['points']} pts, {c['commentaires']} comm." if c.get("points") else ""
            ext = f" (lien : {c['lien_externe']})" if c.get("lien_externe") else ""
            lignes.append(f"- [{c['source']}{extra}, {c['date']}] {c['titre']} : {c['url']}{ext}")
            if c.get("type") == "x":
                lignes.append("  > " + c["texte"].replace("\n", "\n  > "))
            for com in c.get("commentaires_top", []):
                lignes.append(f"  - commentaire de u/{com['auteur']} ({com['score']} pts) : {com['texte'][:300].replace(chr(10), ' ')}")
        lignes.append("")
    (sortie / f"{lundi}.md").write_text("\n".join(lignes), encoding="utf-8")
    print(f"hebdo/veille/{lundi}.md : {len(uniques)} candidats, {len(groupes)} sujets, {len(echecs)} source(s) en échec.")
    if echecs:
        print("Échecs :\n  " + "\n  ".join(echecs), file=sys.stderr)


if __name__ == "__main__":
    main()
