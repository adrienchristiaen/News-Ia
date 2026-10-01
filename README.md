# News IA

Une machine à faire **l'actu IA de la semaine** : une veille semi-automatique, un short vertical de 60 à 90 s pour TikTok, Instagram Reels et YouTube Shorts, et un **journal en ligne** (« La Gazette ») qui reprend le même numéro sous forme de magazine à colonnes avec des illustrations animées.

> Un épisode = un fichier `episodes/<semaine>/episode.json`. Tout le reste (vidéo, site, légendes) est généré à partir de lui.

```
 flux RSS ──► collect ──► rank ──► draft (Claude) ──► episode.json  ◄── tu relis et réécris dans ton ton
                                                          │
                              ┌───────────────────────────┼───────────────────────────┐
                              ▼                           ▼                           ▼
                     voix off (voice.mp3)         video/ (Remotion)              web/ (Next.js)
                     transcribe ► align          short 1080×1920 mp4            La Gazette, statique
                              └──────► timing.json ──►  export ► tiktok / reels / shorts + légende
```

## Démarrage rapide

Prérequis : Python ≥ 3.10, Node ≥ 20, ffmpeg (`brew install ffmpeg`).

```bash
make setup
source .venv/bin/activate

# Voir tout de suite le résultat avec le numéro de démonstration (contenu fictif)
newsia align --week demo-w00
cd video && node render.mjs --week demo-w00 --frames 0-90   # extrait de 3 s → video/out/demo-w00.mp4
cd ../web && npm run dev                                    # http://localhost:3000
```

## Le rituel de la semaine

1. **Veille** : `newsia run` collecte les flux (`config/sources.json`), regroupe les articles qui parlent du même sujet, classe, puis prépare le brouillon.
   - Avec `ANTHROPIC_API_KEY` : le brouillon est généré directement (`NEWSIA_MODEL` pour choisir le modèle).
   - Sans clé : le prompt complet est écrit dans `data/prompts/<semaine>.md` ; colle-le dans Claude, enregistre la réponse, puis `newsia draft --response-file reponse.json`.
2. **Relecture** : ouvre `episodes/<semaine>/episode.json`, vérifie chaque fait dans ses sources, réécris les textes **dans ton ton**. `newsia validate` refuse toute séquence sans source et prévient si la durée dépasse 90 s.
3. **Voix off** : enregistre-toi et dépose `episodes/<semaine>/voice.mp3`. Puis `newsia transcribe` (nécessite `pip install -e "pipeline[speech]"`) et `newsia align` : les sous-titres suivent le rythme réel de ta voix, avec l'orthographe du script. Sans audio, `newsia align` estime le minutage (pratique pour prévisualiser).
4. **Vidéo** : `make video WEEK=2026-w40` puis `make export WEEK=2026-w40` → `out/2026-w40/{tiktok,reels,shorts}.mp4` (volume normalisé) et `legende.txt` (texte, hashtags, sources prêts à coller).
5. **Gazette** : `cd web && npm run build` génère un site 100 % statique dans `web/out/` (Vercel, Netlify, GitHub Pages). Le dernier numéro est en une, les anciens sont dans les archives.

## Organisation

| Dossier | Rôle |
|---|---|
| `config/` | `brand.json` (nom, couleurs, CTA), `sources.json` (flux et mots-clés), `voice.md` (**ton ton**, injecté dans le prompt) |
| `pipeline/` | CLI Python `newsia` : collecte, classement, brouillon, transcription, alignement, validation (8 tests) |
| `episodes/` | un dossier par numéro : `episode.json`, `voice.mp3`, `words.json`, `assets/` (images/vidéos) |
| `video/` | template Remotion « WeeklyShort » : masthead de journal, gravures, sous-titres mot à mot, sources |
| `web/` | La Gazette en Next.js (export statique) |
| `scripts/` | `export.sh` (exports pour les 3 plateformes) |

## Décisions à connaître

- **Le nom est un espace réservé.** « La Gazette de l'Algorithme » est dans `config/brand.json` : change-le à un seul endroit. Évite « Gazette du Sorcier » et « IA Potter » (marques protégées) si tu monétises : garde l'esprit (vieux journal, colonnes, images animées), pas le nom.
- **Illustrations originales, pas de personnalités réelles.** Les gravures sont générées par code (`kind: "engraving"`), sans image externe. Pour des images à toi, mets-les dans `episodes/<semaine>/assets/` et référence-les dans `visual.src` (`kind: "image"` ou `"video"`). Évite les visuels truqués de personnes réelles : les plateformes les sanctionnent et ils peuvent passer pour de vraies images.
- **Aucun fait sans source.** Le prompt interdit d'affirmer ce qui n'est pas dans les sources fournies, et la validation bloque une séquence sans lien. Le brouillon reste un brouillon : c'est toi qui engages ta crédibilité.
- **Format** : 1080×1920, 30 i/s ; les zones réservées par les interfaces des plateformes (haut 150 px, bas 420 px, côtés 70 px) sont respectées dans `video/src/theme.ts`.
- **Les flux RSS de `sources.json` n'ont pas tous été testés en réel** : un flux qui échoue est ignoré avec un avertissement. Ajuste la liste à ta convenance.

## Pistes pour la suite

Sujets récurrents et rubriques fixes, voix clonée **uniquement avec ton accord et la tienne**, publication automatique via les API des plateformes, newsletter à partir de la Gazette, version anglaise.
