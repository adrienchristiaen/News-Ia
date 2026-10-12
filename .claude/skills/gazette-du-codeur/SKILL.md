---
name: gazette-du-codeur
description: Génère le numéro hebdo de La Gazette du Codeur (page, e-mail Gmail, texte Google Chat) à partir du brief ou du fichier d'entrée donné.
---

# La Gazette du Codeur : numéro de la semaine

À utiliser quand on demande « gazette », « génère l'épisode », « numéro de la semaine », ou quand on donne un brief pour la gazette.

## Fichiers (dossier `gazette-du-codeur/` du repo)
- `RECETTE.md` : la recette complète et la ligne éditoriale. **La lire en entier avant d'écrire.** En cas de conflit avec ce skill, RECETTE.md gagne.
- `brief-hebdo-modele.md` : le format du fichier d'entrée.
- `episodes/sXXeYY.json` : un épisode = un fichier JSON. Copier le dernier comme modèle.
- `build.py` produit la page ; `build_email.py` produit l'e-mail et le texte Chat. Dépendances dans `requirements.txt`.

## Entrée
Le fichier ou le texte fourni (brief rempli, notes, liens). En extraire :
- le numéro (s'il manque, prendre le suivant du dernier JSON) ;
- le sujet ;
- les liens de départ ;
- les points à couvrir et ceux à éviter ;
- le contenu des trois rubriques fixes.

Si le brief est vide ou en statut « À REMPLIR », le dire en une ligne et s'arrêter.

## Structure fixe
1. `brief` (« En bref ») : 6 blocs courts. Chacun a un champ `anchor` égal à l'`id` de sa rubrique, ou `une` pour le sujet principal. Dans l'e-mail, ces blocs sont cliquables.
2. `headline` : le sujet de la semaine.
3. Trois articles fixes, toujours présents :
   - `id: "adoption"`, kicker « Dynamique d'adoption » : qui adopte Gemini CLI et comment (chiffres datés et attribués, retours d'équipes).
   - `id: "installation"`, kicker « Installation » : une chose concrète à installer ou à mettre à jour, avec sa commande dans `code`.
   - `id: "rappel"`, kicker « Rappel » : une bonne pratique ou une commande utile mais sous-utilisée.
   Si le brief remplit une rubrique, partir de son contenu ; sinon, chercher soi-même. Chaque rubrique fixe a au moins un bloc dans « En bref ».
4. 0 à 2 articles libres, puis `sources`.

## Règles de rédaction
- Français, ton professionnel, texte court : 2 à 3 paragraphes par rubrique.
- Le lectorat utilise Gemini CLI depuis longtemps : ne pas réexpliquer les bases et ne pas parler d'Antigravity CLI.
- Chaque fait porte une citation `[^idSource]`. Les chiffres d'un éditeur s'écrivent « selon X », avec la date.
- Ne jamais inventer le contenu d'un post X ou d'une vidéo YouTube : passer par une transcription tierce et le dire dans la source.
- Les points non vérifiés vont dans la réponse, pas sur la page.

## Fabrication
1. Écrire `episodes/sXXeYY.json`.
2. Lancer `python3 build.py episodes/sXXeYY.json`, puis `python3 build_email.py episodes/sXXeYY.json`.
3. Vérifier le rendu de la page et de l'e-mail à environ 620 px et 380 px de large. Vérifier aussi que chaque `href="#..."` de « En bref » a sa cible `name=`/`id=`.
4. Copier les fichiers dans `dist/News-IA/<AAAA-MM-JJ>/` :
   - `gazette-sXXeYY.html`
   - `gazette-sXXeYY-email.html`
   - `gazette-sXXeYY-chat.txt`
   - le dossier `email-assets/`
5. Faire un commit avec le message « Gazette sXXeYY ».

## Réponse
Courte : où sont les fichiers, la liste des points non vérifiés, et ce qu'il reste à faire (relire, puis envoyer).
