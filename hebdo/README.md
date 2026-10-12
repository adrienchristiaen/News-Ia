# La Gazette de l'Algorithme : le site hebdo

Un journal de l'IA façon Gazette du sorcier, qui gagne un numéro chaque lundi.
Site : https://adrienchristiaen.github.io/News-Ia/

## Chaque semaine : relire, puis publier

```bash
make gazette                                   # veille + rédaction + vérification -> brouillon (rien n'est publié)
make gazette-relire                            # sert le brouillon sur http://localhost:8001
make gazette-corriger M="retire la brève Meta, la une fait 3 paragraphes de trop"   # autant de fois que nécessaire
make gazette-publier                           # statut publie, commit, push -> le site se met à jour
```

Le brouillon s'affiche avec un encadré « Brouillon à relire » : la liste des points que Claude n'a pas pu confirmer ou te demande de trancher. Tu peux aussi éditer `hebdo/numeros/<lundi>.json` à la main ; `python3 hebdo/build.py --brouillon` revalide. Un brouillon n'apparaît jamais sur le site public, même s'il est poussé.

Variante interactive : ouvre `claude` dans le repo et tape `/gazette-ia`.

## Reddit et X par leurs API officielles

Les clés vont dans `hebdo/.env` (ignoré par git) ou dans l'environnement :

```bash
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
X_BEARER_TOKEN=...
```

- **Reddit (gratuit)** : sur https://www.reddit.com/prefs/apps, « create another app », type **script**, redirect `http://localhost`. L'id est sous le nom de l'app, le secret à côté. La veille lit le top de la semaine des subreddits de `sources.json` et le texte des meilleurs commentaires des 12 posts les plus suivis. Limite : 100 requêtes par minute, la veille en fait une vingtaine. Sans clé, elle tente l'accès public, que Reddit bloque souvent.
- **X (payant à l'usage)** : sur https://console.x.com, crée une app, achète des crédits, copie le *Bearer Token*. Depuis février 2026, l'API X n'a plus d'offre gratuite : environ 0,005 $ par post lu. La veille lit au plus `x.maxPosts` posts (300 par défaut, soit environ 1,50 $ par semaine) des comptes listés dans `sources.json` (`x.comptes`), garde ceux qui dépassent `x.engagementMin`, et donne leur texte intégral et leur lien à Claude, qui peut alors les citer. Sans clé, X est sauté et signalé.

## Comment ça marche

| Fichier | Rôle |
|---|---|
| `veille.py` | Collecte les pistes de la semaine : flux RSS de la presse et des éditeurs, top Reddit et ses meilleurs commentaires, posts X des comptes suivis, fils IA les plus votés de Hacker News. Écrit `veille/<lundi>.md`. |
| `publier.py` | Passe le brouillon en `publie`, revalide, commit et pousse. |
| `sources.json` | La liste des flux, subreddits et mots-clés de la veille. À ajuster librement. |
| `../.claude/skills/gazette-ia/SKILL.md` | La recette éditoriale suivie par Claude : choix, vérification, écriture, publication. |
| `numeros/AAAA-MM-JJ.json` | Un numéro. Le plus récent fait la une ; tous restent dans les archives. |
| `build.py` | Valide les numéros (et `--brouillon` : aperçu local qui les inclut) (citations, sources, dates, typographie) et génère `_site/` : une, `/numero/<date>/`, `/archives/`, `feed.xml`. Python standard, aucune dépendance. |
| `assets/` | Feuille de style, script jour/nuit, polices auto-hébergées (licence OFL). |

Voir le site en local : `make gazette-voir` puis http://localhost:8000.

## Mise en ligne (une seule fois)

Dans GitHub, **Settings → Pages → Build and deployment → Source : GitHub Actions**. Le workflow `.github/workflows/gazette-pages.yml` publie à chaque push sur `main` qui touche `hebdo/`.
GitHub Pages sur un dépôt privé demande un compte GitHub Pro ; sinon, rends le dépôt public ou déploie `hebdo/_site` sur Netlify ou Cloudflare Pages (site statique, rien à configurer).

## Règles qui ne bougent pas

- Aucun fait sans source : chaque phrase factuelle porte une citation `[^id]`, et le build refuse une citation sans source ou une source jamais citée.
- Un post X n'est cité que si la veille l'a lu par l'API ; sinon il n'est jamais résumé.
- Rien n'est publié sans ton `make gazette-publier`.
- Le nom du journal, la devise et l'URL du site se changent dans `config/brand.json`.
