---
name: gazette-ia
description: Rédige et publie le numéro hebdomadaire de La Gazette de l'Algorithme (site de news IA façon Gazette du sorcier, dossier hebdo/). À utiliser pour « numéro de la semaine », « gazette IA », « nouveau numéro », make gazette.
---

# La Gazette de l'Algorithme : le numéro de la semaine

Un numéro paraît chaque lundi et couvre la semaine du lundi au dimanche précédents. Tout se passe dans `hebdo/`.
Le travail est entièrement autonome : ne pose pas de question, va jusqu'au commit.

## 1. Cadrer
- Date de parution : le lundi de cette semaine si l'on est lundi, sinon le lundi qui vient (ou la date donnée en argument). Période : les 7 jours qui précèdent.
- Numéro : celui du dernier fichier de `hebdo/numeros/` plus 1. Si un fichier existe déjà pour cette date, le mettre à jour au lieu d'en créer un second.
- Lire les deux derniers numéros pour le ton et la structure, et ne pas redonner une nouvelle déjà traitée sauf fait nouveau.

## 2. Ratisser
1. `python3 hebdo/veille.py --date <lundi>` puis lire `hebdo/veille/<lundi>.md` : flux de la presse et des éditeurs, top Reddit de la semaine, fils IA les plus votés de Hacker News, regroupés par sujet et classés.
2. Compléter par WebSearch (plusieurs requêtes dans le même tour) : « AI news this week <dates> », annonces OpenAI, Anthropic, Google, Meta, Mistral, xAI, DeepSeek et Qwen, régulation (UE, États-Unis), recherche marquante, levées de fonds majeures, et les revues de presse quotidiennes (aiweekly.co, the-decoder.com).
3. X (Twitter) n'est pas lisible directement : repérer ses débats via la presse, Hacker News et Reddit, et ne jamais citer le contenu d'un post qu'on n'a pas lu. Pour une vidéo YouTube, passer par une transcription tierce et le dire dans la source.
4. Si une source de la veille est injoignable (Reddit bloque parfois), continuer avec les autres et le noter pour la réponse finale.

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
- Jamais de fait, de citation ou de chiffre inventé. Ce qui n'a pas pu être vérifié ne va pas sur la page : il va dans la réponse finale.

## 5. Écrire `hebdo/numeros/<lundi>.json`
Copier la structure du dernier numéro. Champs : `numero`, `date`, `periode {du, au}`, `resume` (une phrase pour les archives et le RSS), `une`, `articles`, `breves`, `salleCommune`, `sources`.
- Français, ton de journal sérieux : l'univers Harry Potter est dans la maquette (titre gothique, Hiboux express, salle commune), pas dans les faits. Pas de jeux de mots forcés.
- Titres courts et informatifs ; `titreCourt` (4 mots environ) pour le sommaire. Chapô d'une ou deux phrases. Corps : 2 à 4 paragraphes courts par article, 3 pour la une.
- Chaque fait porte une citation `[^idSource]` ; chaque source listée est citée. Balisage autorisé : `code`, **gras**, *italique*, [lien](https://…).
- Pas de tiret cadratin ni demi-cadratin (le build les refuse) : virgule, deux-points ou parenthèses. Pas d'espace avant les deux-points dans les titres anglais cités tels quels.
- Citations en anglais : les traduire et ajouter « (traduit) » dans l'attribution.

## 6. Construire et publier
1. `python3 hebdo/build.py` : il valide le numéro (citations, sources, date, tirets) puis génère `hebdo/_site/`. Corriger jusqu'à ce qu'il passe.
2. Ouvrir `hebdo/_site/index.html` (ou servir le dossier) et vérifier en largeur bureau et mobile si un navigateur est disponible.
3. `git add hebdo/numeros/<lundi>.json` puis commit « Gazette n°N, <lundi> » et `git push` sur la branche par défaut : GitHub Actions publie le site sur GitHub Pages.

## 7. Répondre
Court : le titre de la une, le lien du site, la liste des points non vérifiés ou écartés, et les sources de la veille qui étaient injoignables.
