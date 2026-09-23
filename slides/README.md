# Slide deck: Economic Scenarios for Transformative AI

A step-by-step walkthrough of Korinek, Jones, Sacher, Cotter and McCrory (2026):
the main claim first, then the model that produces it, then how that model is solved
for US inputs, then the results.

Built in the authoring style of the sibling `courses/` repos: xaringan, the shared
YAML and CSS block, `.highlight-box` / `.blue-box`, named anchors with backup slides
at the end for derivations. It is a standalone deck rather than a course module, so
it has no Course Map slide (a Deck Map takes that slot) and no `concepts.md` /
`exercise.R` companions.

## Structure

81 slides: the xaringan title slide, "An Open Reproduction" (the OPA framing and links to
the other artifacts), a Deck Map, then four parts and the backups.

| Part | Slides | Covers |
|---|---|---|
| 1. The claim | 4-18 | What the paper asserts, the terminology this deck does not borrow, one slide per input, and the model on one page |
| 2. The model | 19-34 | Task production, the assignment rule, prices and shares, TFP, the labor share, employment, ideas, unemployment: where every equation comes from |
| 3. Solving the model for US inputs | 35-48 | Calibration, the steady state, month zero, the two 44-equation walls, the (39) inversion, the root-finds |
| 4. Results: some scenarios and the explorer | 49-61 | The three scenarios one at a time, robustness, the survey, what reproduces, takeaways, and two postscripts (the seven-input grid, the slop extension) |
| Backup | 62-81 | Derivations, month 0 step by step, matching, the gain *a*, the U-bar cells |

Cross-references inside the deck use `name:` anchors rather than slide numbers, because
the numbering moves whenever a slide is inserted. The Deck Map on slide 3 is the one
place numbers appear, and it has to be re-checked after any structural change.

## Rebuilding

The deck's tables and figures hold no transcribed model outputs: they read CSVs exported
by the Python model in the parent directory. A few reproduced values are quoted in prose
(the U-bar gaps on the verification slide and its backup, the test and cell counts) and
have to be re-checked by hand if the model changes. Three exporters feed it.

```sh
cd ..
python3 run.py --csv slides/data      # data/{modest,substantial,extreme}.csv,
                                      # data/table{3,5,6}.csv and data/slop.csv
python3 slides/make_grid.py           # data/grid.csv, the 3^7 factorial (~16 s)
python3 slides/make_inputs.py         # data/inputs.csv, the seven inputs at 2030
cd slides
RSTUDIO_PANDOC=/Applications/quarto/bin/tools/aarch64 \
  Rscript -e 'rmarkdown::render("slides.Rmd", quiet = TRUE)'
```

`slides/make_grid_app.py` and `slides/make_month0.py` live here too, but neither feeds
the deck: the first builds the scenario explorer's `explorer/grid.js`, and the second
writes `data/month0.csv` for reference while working on the month-zero backup slides.

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
