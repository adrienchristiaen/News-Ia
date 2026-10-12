---
name: gazette-ia
description: Rédige le brouillon (puis applique les corrections) du numéro hebdomadaire de La Gazette de l'Algorithme (site de news IA façon Gazette du sorcier, dossier hebdo/). À utiliser pour « numéro de la semaine », « gazette IA », « nouveau numéro », make gazette.
---

# La Gazette de l'Algorithme : le numéro de la semaine

Un numéro paraît chaque lundi et couvre la semaine du lundi au dimanche précédents. Tout se passe dans `hebdo/`.
Le travail est autonome (ne pose pas de question) mais **ne publie jamais** : il produit un brouillon que le rédacteur en chef relit, corrige avec `make gazette-corriger M="…"` et publie lui-même avec `make gazette-publier`.

Deux modes :
- **Brouillon** (par défaut, `make gazette`) : étapes 1 à 7.
- **Corrections** (le prompt contient « mode corrections ») : seulement l'étape 8.

## 1. Cadrer
- Date de parution : le lundi de cette semaine si l'on est lundi, sinon le lundi qui vient (ou la date donnée en argument). Période : les 7 jours qui précèdent.
- Numéro : celui du dernier fichier de `hebdo/numeros/` plus 1. Si un fichier existe déjà pour cette date, le mettre à jour au lieu d'en créer un second.
- Lire les deux derniers numéros pour le ton et la structure, et ne pas redonner une nouvelle déjà traitée sauf fait nouveau.

## 2. Ratisser
1. `python3 hebdo/veille.py --date <lundi>` puis lire `hebdo/veille/<lundi>.md` : flux de la presse et des éditeurs, top Reddit de la semaine avec le texte des meilleurs commentaires (API officielle), posts X des comptes suivis avec leur texte intégral (API X v2, si la clé existe), fils IA les plus votés de Hacker News, regroupés par sujet et classés.
2. Compléter par WebSearch (plusieurs requêtes dans le même tour) : « AI news this week <dates> », annonces OpenAI, Anthropic, Google, Meta, Mistral, xAI, DeepSeek et Qwen, régulation (UE, États-Unis), recherche marquante, levées de fonds majeures, et les revues de presse quotidiennes (aiweekly.co, the-decoder.com).
3. X : un post récupéré par l'API (texte dans la veille, URL `x.com/<compte>/status/<id>`) est une source citable, avec `editeur` « X, @compte ». Un post qui n'est pas dans la veille n'est jamais cité ni résumé sans avoir été lu. Une annonce faite sur X se recoupe avec la page officielle quand elle existe. Pour une vidéo YouTube, passer par une transcription tierce et le dire dans la source.
4. Reddit : les commentaires servent à mesurer la réaction de la communauté (« Sur r/LocalLLaMA, les premiers tests… ») ; un commentaire n'est jamais une preuve d'un fait.
5. Si une source de la veille est injoignable ou sans clé (la veille l'indique), continuer avec les autres et l'ajouter à `relecture`.

## 3. Choisir
Lectorat : des gens du métier, francophones, pressés. Ce qui compte, c'est ce qui change leurs outils, leurs coûts ou leur compréhension du domaine. Le bruit marketing et les rumeurs non sourcées sont écartés.
- **À la une** : LE sujet de la semaine (le plus important, pas le plus bruyant), avec une `figure` : de préférence un `chiffre` qui résume l'enjeu, sinon une `citation`.
- **4 articles** (`articles`, 3 à 5) : modèles, produits, prix, open source, agents, régulation, recherche. Un article peut fusionner deux nouvelles liées. Le 4e (ou un autre) peut porter une `citation` en exergue.
- **Hiboux express** (`breves`, 4 à 6) : une nouvelle utile en 2 ou 3 phrases.
- **La salle commune** (`salleCommune`, 4 à 6) : les fils les plus discutés de la semaine (Hacker News, Reddit), avec points et commentaires relevés le jour de la rédaction et une note d'une phrase.

## 4. Vérifier
Chaque fait est vérifié à sa source avec WebFetch avant d'être écrit : annonce officielle, documentation ou dépôt d'abord, presse reconnue ensuite, agrégateurs seulement en dernier recours (et alors l'indiquer dans `editeur`, par exemple « AI Weekly, d'après The Decoder »).
- Chiffres d'un éditeur : « selon Anthropic », avec la date. Benchmarks d'un éditeur : préciser que ce sont ses chiffres.
- En cas de désaccord entre sources, garder la version de la source primaire ou ne pas donner le chiffre.
- Jamais de fait, de citation ou de chiffre inventé. Ce qui n'a pas pu être vérifié du tout ne va pas sur la page. Ce qui est vérifié mais fragile (une seule source, chiffre d'éditeur non recoupé, date non officielle, sujet écarté de justesse) va sur la page **et** dans `relecture`, pour que le rédacteur en chef tranche.

## 5. Écrire `hebdo/numeros/<lundi>.json`
Copier la structure du dernier numéro. Champs : `numero`, `date`, `periode {du, au}`, `statut` (toujours `"brouillon"` ici), `relecture` (liste de phrases courtes : chaque point à trancher, en nommant l'article concerné ; liste vide s'il n'y a rien), `resume` (une phrase pour les archives et le RSS), `une`, `articles`, `breves`, `salleCommune`, `sources`.
- Français, ton de journal sérieux : l'univers Harry Potter est dans la maquette (titre gothique, Hiboux express, salle commune), pas dans les faits. Pas de jeux de mots forcés.
- Titres courts et informatifs ; `titreCourt` (4 mots environ) pour le sommaire. Chapô d'une ou deux phrases. Corps : 2 à 4 paragraphes courts par article, 3 pour la une.
- Chaque fait porte une citation `[^idSource]` ; chaque source listée est citée. Balisage autorisé : `code`, **gras**, *italique*, [lien](https://…).
- Pas de tiret cadratin ni demi-cadratin (le build les refuse) : virgule, deux-points ou parenthèses. Pas d'espace avant les deux-points dans les titres anglais cités tels quels.
- Citations en anglais : les traduire et ajouter « (traduit) » dans l'attribution.

## 6. Construire le brouillon
1. `python3 hebdo/build.py --brouillon` : il valide le numéro (citations, sources, date, tirets) puis génère `hebdo/_brouillon/`, où le brouillon apparaît avec un encadré « Brouillon à relire » qui liste `relecture`. Corriger jusqu'à ce qu'il passe.
2. Vérifier `hebdo/_brouillon/index.html` en largeur bureau et mobile si un navigateur est disponible.
3. Ne pas commit, ne pas pousser : la publication appartient au rédacteur en chef.

## 7. Répondre
Court : le titre de la une, les points de `relecture`, les sources de la veille injoignables, puis les deux commandes : `make gazette-corriger M="…"` et `make gazette-publier`.

## 8. Mode corrections
Le prompt contient les corrections du rédacteur en chef, en langage libre (« retire la brève Meta », « le chiffre de la une est faux, c'est 38 % », « ajoute un article sur X », « ton trop sec »).
1. Ouvrir le brouillon le plus récent de `hebdo/numeros/` (`statut` = `brouillon`).
2. Appliquer chaque correction. Un fait ajouté ou modifié se vérifie à sa source comme à l'étape 4, avec sa citation ; si la correction contredit une source, appliquer la correction (le rédacteur en chef peut savoir mieux) mais le signaler dans la réponse. Retirer une source qui n'est plus citée.
3. Retirer de `relecture` les points que la correction tranche ; en ajouter si la correction en crée.
4. `python3 hebdo/build.py --brouillon` jusqu'à ce qu'il passe. Ne pas publier.
5. Répondre en une liste : ce qui a changé, ce qui reste dans `relecture`.
