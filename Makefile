THESIS ?= thesis
LATEXMK ?= latexmk
TLMGR ?= tlmgr
BUILD_DIR ?= build/latex
UV_PROJECT_ENVIRONMENT ?= /private/tmp/diploma-bench-venv

BUILT_PDF = $(BUILD_DIR)/$(THESIS).pdf
PDF = $(THESIS).pdf
TEXLIVE_PACKAGES = \
	latexmk biber \
	collection-latexrecommended collection-latexextra collection-fontsrecommended \
	collection-bibtexextra collection-pictures
TEX_REQUIRED_COMMANDS = latexmk pdflatex biber kpsewhich
TEX_REQUIRED_FILES = \
	extreport.cls tgtermes.sty vmargin.sty setspace.sty indentfirst.sty cmap.sty \
	biblatex.sty pdfpages.sty amsmath.sty amsthm.sty float.sty graphicx.sty \
	multirow.sty caption.sty subcaption.sty paralist.sty listings.sty zed-csp.sty \
	fancyhdr.sty csquotes.sty chngcntr.sty upgreek.sty bm.sty booktabs.sty \
	longtable.sty pgfplots.sty tabularx.sty pdflscape.sty enumitem.sty hyperref.sty

.PHONY: all pdf build watch doctor install-tex-deps clean distclean test-bench help

all: pdf

pdf build: doctor
	$(LATEXMK) -pdf -outdir=$(BUILD_DIR) $(THESIS).tex
	cp $(BUILT_PDF) $(PDF)

watch: doctor
	$(LATEXMK) -pdf -pvc -outdir=$(BUILD_DIR) \
		-e '$$success_cmd = q{cp $(BUILT_PDF) $(PDF)};' $(THESIS).tex

doctor:
	@missing=0; \
	for cmd in $(TEX_REQUIRED_COMMANDS); do \
		if ! command -v $$cmd >/dev/null 2>&1; then \
			printf 'missing command: %s\n' "$$cmd"; \
			missing=1; \
		fi; \
	done; \
	if command -v kpsewhich >/dev/null 2>&1; then \
		for file in $(TEX_REQUIRED_FILES); do \
			if ! kpsewhich $$file >/dev/null 2>&1; then \
				printf 'missing TeX file: %s\n' "$$file"; \
				missing=1; \
			fi; \
		done; \
	fi; \
	if [ $$missing -ne 0 ]; then \
		printf '\nInstall missing TeX packages with:\n  sudo tlmgr install $(TEXLIVE_PACKAGES)\n'; \
	fi; \
	exit $$missing

install-tex-deps:
	$(TLMGR) install $(TEXLIVE_PACKAGES)

clean:
	@if command -v $(LATEXMK) >/dev/null 2>&1; then \
		$(LATEXMK) -c -outdir=$(BUILD_DIR) $(THESIS).tex; \
	fi
	rm -rf $(BUILD_DIR)
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.ruff_cache' -o -name '.mypy_cache' \) -prune -exec rm -rf {} +

distclean: clean
	@if command -v $(LATEXMK) >/dev/null 2>&1; then \
		$(LATEXMK) -C -outdir=$(BUILD_DIR) $(THESIS).tex; \
	fi
	rm -f $(PDF)
	rm -rf build dist

test-bench:
	cd benchmarks && UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run pytest

help:
	@printf '%s\n' \
	  'make pdf        Build build/latex/thesis.pdf and copy thesis.pdf to project root' \
	  'make watch      Rebuild continuously and refresh thesis.pdf after successful builds' \
	  'make doctor     Check required TeX commands and style files' \
	  'make install-tex-deps  Install known TeX Live packages; use TLMGR="sudo tlmgr" if needed' \
	  'make clean      Remove generated LaTeX/cache files, keep thesis.pdf' \
	  'make distclean  Remove generated files and thesis.pdf' \
	  'make test-bench Run benchmark tests with a temporary uv environment'
