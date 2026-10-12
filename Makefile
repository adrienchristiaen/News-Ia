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

gazette:         ## LA commande hebdo : veille, rédaction et vérification -> brouillon à relire (rien n'est publié)
	git pull --rebase --autostash
	claude -p "Utilise le skill gazette-ia pour produire le brouillon du numéro de cette semaine." \
	  --permission-mode acceptEdits --allowedTools $(GAZETTE_OUTILS)
	python3 hebdo/build.py --brouillon
	@echo "\nBrouillon : hebdo/_brouillon/index.html  (make gazette-relire pour le servir)"

gazette-relire:  ## sert le brouillon sur http://localhost:8001
	python3 hebdo/build.py --brouillon && python3 -m http.server 8001 -d hebdo/_brouillon

gazette-corriger: ## applique tes corrections au brouillon : make gazette-corriger M="retire la brève Meta, la une est trop longue"
	@test -n "$(M)" || (echo 'Usage : make gazette-corriger M="tes corrections"' && exit 1)
	claude -p "Utilise le skill gazette-ia en mode corrections. Corrections demandées par le rédacteur en chef : $(M)" \
	  --permission-mode acceptEdits --allowedTools $(GAZETTE_OUTILS)
	python3 hebdo/build.py --brouillon

gazette-publier: ## publie le brouillon relu (statut publie, commit, push -> GitHub Pages)
	python3 hebdo/publier.py

GAZETTE_OUTILS = "WebSearch" "WebFetch" "Read" "Write" "Edit" "Glob" "Grep" "Bash(python3 hebdo/*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(git log:*)"

gazette-site:    ## reconstruit le site de la gazette dans hebdo/_site
	python3 hebdo/build.py

gazette-voir:    ## construit puis sert le site sur http://localhost:8000
	python3 hebdo/build.py && python3 -m http.server 8000 -d hebdo/_site

.PHONY: help setup test veille align video export site gazette gazette-relire gazette-corriger gazette-publier gazette-site gazette-voir
