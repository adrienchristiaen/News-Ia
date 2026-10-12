# La Gazette de l'Algorithme : le site hebdo

Un journal de l'IA façon Gazette du sorcier, qui gagne un numéro chaque lundi.
Site : https://adrienchristiaen.github.io/News-Ia/

## Chaque semaine : une commande

```bash
make gazette
```

Claude Code (le CLI `claude`, connecté à ton compte) lance la veille, choisit les sujets, vérifie chaque fait à la source, écrit `hebdo/numeros/<lundi>.json`, construit le site, commit et pousse. GitHub Actions publie ensuite le site. À la fin, il affiche la une et la liste de ce qu'il n'a pas pu vérifier.

Variante interactive : ouvre `claude` dans le repo et tape `/gazette-ia`.

## Comment ça marche

| Fichier | Rôle |
|---|---|
| `veille.py` | Collecte les pistes de la semaine : flux RSS de la presse et des éditeurs, top Reddit, fils IA les plus votés de Hacker News. Écrit `veille/<lundi>.md`. |
| `sources.json` | La liste des flux, subreddits et mots-clés de la veille. À ajuster librement. |
| `../.claude/skills/gazette-ia/SKILL.md` | La recette éditoriale suivie par Claude : choix, vérification, écriture, publication. |
| `numeros/AAAA-MM-JJ.json` | Un numéro. Le plus récent fait la une ; tous restent dans les archives. |
| `build.py` | Valide les numéros (citations, sources, dates, typographie) et génère `_site/` : une, `/numero/<date>/`, `/archives/`, `feed.xml`. Python standard, aucune dépendance. |
| `assets/` | Feuille de style, script jour/nuit, polices auto-hébergées (licence OFL). |

Voir le site en local : `make gazette-voir` puis http://localhost:8000.

## Mise en ligne (une seule fois)

Dans GitHub, **Settings → Pages → Build and deployment → Source : GitHub Actions**. Le workflow `.github/workflows/gazette-pages.yml` publie à chaque push sur `main` qui touche `hebdo/`.
GitHub Pages sur un dépôt privé demande un compte GitHub Pro ; sinon, rends le dépôt public ou déploie `hebdo/_site` sur Netlify ou Cloudflare Pages (site statique, rien à configurer).

## Règles qui ne bougent pas

- Aucun fait sans source : chaque phrase factuelle porte une citation `[^id]`, et le build refuse une citation sans source ou une source jamais citée.
- Les posts X ne se lisent pas automatiquement : ils ne sont jamais résumés sans avoir été lus.
- Le nom du journal, la devise et l'URL du site se changent dans `config/brand.json`.
