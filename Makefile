# Raccourcis. `make help` liste les commandes.
WEEK ?= $(shell newsia week 2>/dev/null)

help:            ## cette aide
	@grep -E '^[a-z-]+:.*##' Makefile | sed 's/:.*##/\t/'

setup:           ## installe tout (Python, Remotion, Next.js)
	python3 -m venv .venv && .venv/bin/pip install -e "pipeline[dev,llm]"
	cd video && npm install
	cd web && npm install

test:            ## tests Python + typecheck vidéo + build du site
	.venv/bin/python -m pytest -q pipeline
	cd video && npx tsc --noEmit -p .
	cd web && npm run build

veille:          ## collecte + tri + brouillon de la semaine
	.venv/bin/newsia run

align:           ## calcule le minutage (WEEK=2026-w40)
	.venv/bin/newsia align --week $(WEEK)

video:           ## rend le short en mp4 (WEEK=2026-w40)
	cd video && node render.mjs --week $(WEEK)

export:          ## prépare tiktok/reels/shorts + légende
	scripts/export.sh $(WEEK)

site:            ## site en local
	cd web && npm run dev

gazette:         ## LA commande hebdo : veille, rédaction, vérification, build et publication du numéro
	git pull --rebase --autostash
	claude -p "Utilise le skill gazette-ia pour produire et publier le numéro de cette semaine." \
	  --permission-mode acceptEdits \
	  --allowedTools "WebSearch" "WebFetch" "Read" "Write" "Edit" "Glob" "Grep" \
	    "Bash(python3 hebdo/*)" "Bash(git add:*)" "Bash(git commit:*)" "Bash(git push:*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(git log:*)"

gazette-site:    ## reconstruit le site de la gazette dans hebdo/_site
	python3 hebdo/build.py

gazette-voir:    ## construit puis sert le site sur http://localhost:8000
	python3 hebdo/build.py && python3 -m http.server 8000 -d hebdo/_site

.PHONY: help setup test veille align video export site gazette gazette-site gazette-voir
