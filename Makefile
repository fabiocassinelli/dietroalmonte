# Dietro al Monte — comandi quotidiani
.PHONY: aiuto csl anteprima costruisci nuova timbra pubblica rilascia pulisci controlla

SLUG ?=
MSG  ?= Aggiornamento
VER  ?= 1.0

aiuto:
	@echo "make csl                      scarica Chicago come stile alternativo"
	@echo "make nuova SLUG=rossi-scurtabo   apre una nuova ricerca"
	@echo "make anteprima                anteprima locale con ricarica automatica"
	@echo "make costruisci               costruisce il sito in _site/"
	@echo "make timbra SLUG=rossi-scurtabo  marca temporale OpenTimestamps"
	@echo "make pubblica MSG=\"...\"        commit firmato + push (sito online)"
	@echo "make rilascia SLUG=... VER=1.0   tag firmato -> Release -> DOI Zenodo"
	@echo "make controlla                verifica firme e marche temporali"

csl:
	@mkdir -p assets/csl
	@curl -fsSL -o assets/csl/chicago-notes-bibliography.csl \
	  https://raw.githubusercontent.com/citation-style-language/styles/master/chicago-notes-bibliography.csl
	@echo "Scaricato lo stile Chicago come alternativa."
	@echo "Per usarlo, cambia la chiave csl: in _quarto.yml."

anteprima:
	quarto preview

costruisci:
	quarto render

nuova:
	@test -n "$(SLUG)" || { echo "Manca SLUG. Esempio: make nuova SLUG=rossi-scurtabo"; exit 1; }
	@./scripts/nuova-ricerca.sh $(SLUG)

timbra:
	@test -n "$(SLUG)" || { echo "Manca SLUG."; exit 1; }
	@./scripts/timbra.sh $$(find ricerche -maxdepth 1 -type d -name "*$(SLUG)" | head -n1)

pubblica:
	@# _revisioni.md si rigenera a ogni render: resta a zero byte nel
	@# repository e viene ricostruito da GitHub Actions prima di pubblicare.
	git add -A -- . ':!ricerche/*/_revisioni.md'
	git commit -S -m "$(MSG)"
	git push
	@echo "Il sito si ricostruisce da solo. Fra circa 90 secondi è online."

rilascia:
	@test -n "$(SLUG)" || { echo "Manca SLUG."; exit 1; }
	git tag -s v$(VER)-$(SLUG) -m "$(SLUG), versione $(VER)"
	git push --tags
	@echo "Tag inviato. GitHub crea la Release, Zenodo assegna il DOI."
	@echo "Quando il DOI è pronto, mettilo nel front matter e ripubblica."

controlla:
	@echo "── Firme delle ultime 10 modifiche ──"
	@git log -10 --show-signature --format='%h %G? %an %ad %s' --date=short || true
	@echo
	@echo "── Marche temporali ──"
	@find ricerche -name '*.ots' -exec sh -c 'echo; echo "$$1"; ots verify "$$1" 2>&1 | tail -3' _ {} \;

pulisci:
	rm -rf _site .quarto
	find ricerche -name '_revisioni.md' -exec sh -c ': > "$$1"' _ {} \;
