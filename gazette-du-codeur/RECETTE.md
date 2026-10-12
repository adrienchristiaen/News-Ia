# La Gazette du Codeur (ex-IA Potter) : recette d'un épisode

Dire à Claude : « génère l'épisode N » (optionnellement avec le sujet et des liens de départ).

## Fichiers
- `template/gazette.html` : la maquette Daily Prophet (ne pas toucher pour un épisode normal).
- `episodes/sXXeYY.json` : le contenu d'un épisode. Copier le dernier épisode comme modèle.
- `media/` : clips courts (webm/mp4/gif/webp, moins de 4 Mo chacun), intégrés au build.
- `build.py` : `python3 build.py episodes/s01e02.json` produit `dist/s01e02.html`.

## Étapes
1. Sujet : celui donné par Adrien, sinon l'actualité IA de la semaine la plus utile aux développeurs.
2. Sources, par ordre de confiance :
   - officielles : docs produit, changelogs, dépôts GitHub, blogs des éditeurs ;
   - praticiens reconnus (posts, blogs, talks) ;
   - presse tech en appui seulement.
   Les posts X ne sont pas lisibles automatiquement : les lister dans l'encadré `"kind": "unverified"`
   sans inventer leur contenu, ou demander à Adrien de coller le texte.
3. Écrire le JSON en français : `headline`, `sideStory`, 2 à 4 `articles` (rangées de 6 unités :
   `large` = 4, `medium` = 2), 3 `boxes`, `ads`, `index`, `sources`.
   Chaque fait porte une citation `[^idSource]` ; `build.py` refuse une citation sans source.
   Chiffres annoncés par un éditeur : le dire (« selon Google »), avec la date.
4. Images animées : `{"type":"scene","name":"choixpeau|eclair|hibou|terminal"}`
   (`terminal` accepte `"lines": [...]`), ou `{"type":"video","src":"media/clip.webm"}`,
   ou `{"type":"image","src":"media/anim.gif"}`. Les URL externes ne s'affichent pas : télécharger en local.
5. `python3 build.py episodes/sXXeYY.json`, vérifier la page, publier `dist/sXXeYY.html` comme Artifact
   (un Artifact par épisode), puis répondre avec le lien et la liste des points non vérifiés.

## Ligne éditoriale (retour d'Adrien, 12 oct. 2026)
- Lecteurs : utilisateurs de longue date de Gemini CLI. Ne pas réexpliquer le fonctionnement de base ni les modèles disponibles.
- Contenu court et léger : techniques peu connues, retours de praticiens (Reddit/X) quand ils sont vérifiables, sous-agents, gestion du contexte et des conversations, réglages de compression, commandes, skills utiles.
- Ne jamais présenter une astuce comme issue de Reddit/X sans l'avoir lue à la source.
- Format digeste : la majorité des lecteurs n'ont pas le temps de lire long. Résumer les mouvements, phrases courtes, 2 à 3 paragraphes par rubrique, un encadré « En un coup d'œil ».
- Ne pas parler d'Antigravity CLI : le lectorat reste sur Gemini CLI. Pas d'encadré « non vérifié » sur la page : les points non vérifiés vont dans la réponse à Adrien.
- Les posts X et YouTube ne se lisent pas directement : chercher une transcription ou un résumé tiers (ex. usetranscribe.io/yt/<id>) et le dire dans la source.
- Ton professionnel : pas de prix, pas de petites annonces, pas de rubriques humoristiques. Garder seulement le style visuel du journal. Ajouter en haut un bloc « En bref » (champ `brief`, 6 blocs courts avec lien vers la rubrique) et numéroter l'épisode « S01EP01 » avec un titre.
- Rubriques fixes chaque semaine (demande d'Adrien, 12 oct. 2026) : « Dynamique d'adoption », « Installation », « Rappel ». Chacune est un article (`id` : `adoption`, `installation`, `rappel`) et a son bloc dans « En bref ». Le skill `gazette-du-codeur` applique cette recette.
- E-mail : les blocs « En bref » sont des liens d'ancre vers leur rubrique (`anchor` = `id` de l'article, ou `une`).
