# Slide deck: Economic Scenarios for Transformative AI

A step-by-step walkthrough of Korinek, Jones, Sacher, Cotter and McCrory (2026):
the main claim first, then the theory that produces it, then the machinery.

Built in the authoring style of the sibling `courses/` repos: xaringan, the shared
YAML and CSS block, `.highlight-box` / `.blue-box`, named anchors with backup slides
at the end for derivations. It is a standalone deck rather than a course module, so
it has no Course Map slide (a Deck Map takes that slot) and no `concepts.md` /
`exercise.R` companions.

## Structure

| Part | Slides | Covers |
|---|---|---|
| 1. The claim | 2-5 | What the paper asserts; what kind of object a scenario is |
| 2. Theory, the level channel | 6-15 | Task-based production, prices, TFP, the labor share, employment targets, Proposition 1 |
| 3. Growth and unemployment | 16-21 | Semi-endogenous ideas; rigid wages, rationing, search and matching |
| 4. Methods | 22-26 | Calibration sources, the monthly solution algorithm |
| 5. Results and trust | 27-37 | Scenario by scenario, robustness, the survey, what reproduces |
| Backup | 38-46 | CES refresher, share derivation, labor-share and wage-line derivations, the so-so-automation threshold, matching, the U-bar discrepancy |

## Rebuilding

The deck holds no transcribed numbers: it reads CSVs exported by the Python model in
the parent directory.

```sh
cd ..
python3 run.py --csv slides/data      # refresh data/{modest,substantial,extreme}.csv
                                      # and data/table{3,5,6}.csv
cd slides
RSTUDIO_PANDOC=/Applications/quarto/bin/tools/aarch64 \
  Rscript -e 'rmarkdown::render("slides.Rmd", quiet = TRUE)'
```

`slides.html` is a thin loader: it pulls remark.js from a CDN and references
`slides_files/figure-html/*.png`, so a successful render means both exist, not that
the HTML is large. Viewing it needs an internet connection.

To check it visually, print to PDF rather than screenshotting, since a screenshot
captures only the current increment:

```sh
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --virtual-time-budget=25000 \
  --run-all-compositor-stages-before-draw \
  --print-to-pdf=/tmp/slides.pdf "file://$PWD/slides.html?print-pdf"
```
