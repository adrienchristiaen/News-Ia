# La Gazette du Codeur

Newsletter hebdo pour les utilisateurs de Gemini CLI, au style journal ancien. Chaque numéro sort en trois formats : une page web, un e-mail Gmail et un texte pour Google Chat.

## Installation

```bash
cd gazette-du-codeur
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium   # sauf si GAZETTE_CHROME pointe vers un Chromium existant
```

## Fabriquer un numéro

```bash
python3 build.py episodes/s01e02.json         # page : dist/s01e02.html
python3 build_email.py episodes/s01e02.json   # e-mail + texte Chat : dist/s01e02-email.html, dist/s01e02-chat.txt
```

Ensuite, copier les trois fichiers et `dist/email-assets/` dans `dist/News-IA/<AAAA-MM-JJ>/`. C'est le seul dossier de `dist/` suivi par git.

Avec Claude Code, ouvrir le repo et dire « gazette » en donnant le brief rempli : le skill `.claude/skills/gazette-du-codeur` fait tout. La recette complète et la ligne éditoriale sont dans `RECETTE.md`, et le format du brief dans `brief-hebdo-modele.md`.

## Rubriques fixes

Chaque semaine : Dynamique d'adoption, Installation et Rappel, en plus du sujet de la semaine.
