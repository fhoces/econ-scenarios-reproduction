# Build targets for the reproduction. The explicit commands are in README.md, "Usage".
#
# Two tool paths come from the environment, with fallbacks that work when the right
# python3 and pandoc are already on PATH. Override them when they are not, e.g.
#   make report QUARTO_PYTHON=/opt/anaconda3/bin/python3
#   make slides RSTUDIO_PANDOC=/Applications/quarto/bin/tools/aarch64
# QUARTO_PYTHON must be an interpreter with pandas, matplotlib and tabulate installed;
# RSTUDIO_PANDOC is the directory holding the pandoc binary (the one bundled with
# Quarto or RStudio is fine).
QUARTO_PYTHON ?= $(shell command -v python3)
RSTUDIO_PANDOC ?= $(shell dirname $$(command -v pandoc) 2>/dev/null)
PYTHON ?= python3

.PHONY: all test csv report slides grid

all: test csv report grid slides

test:                       ## the 128-test validation suite
	$(PYTHON) -m pytest -q

csv:                        ## the CSVs the deck reads (slides/data/)
	$(PYTHON) run.py --csv slides/data

report:                     ## repro.qmd -> repro.html
	QUARTO_PYTHON=$(QUARTO_PYTHON) quarto render repro.qmd

grid:                       ## the explorer's precomputed grid (explorer/grid.js, ~30 s)
	$(PYTHON) slides/make_grid_app.py

slides:                     ## slides/slides.Rmd -> slides/slides.html
	cd slides && $(if $(RSTUDIO_PANDOC),RSTUDIO_PANDOC=$(RSTUDIO_PANDOC),) Rscript -e 'rmarkdown::render("slides.Rmd", quiet = TRUE)'
