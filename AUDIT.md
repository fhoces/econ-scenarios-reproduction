# OPA self-audit, 2026-09-24

Scored against the BITSS OPA Guidelines (2019), nine steps, levels 0 to 3, at commit
`97e6e32` (tag `v1.0` plus the step 1 rewording in `477593d` and the CI workflow in
`97e6e32`). Level wording is quoted from the Guidelines. The repository
`fhoces/opa-ai-macro-econ-scenarios` is public and served on GitHub Pages.

This project reproduces a published paper (Korinek et al. 2026) rather than presenting an
original policy analysis. Where that changes the reading of a step, the row says so.

| # | Step | Level | Evidence | What the next level needs |
|---|---|---|---|---|
| 1 | Unified output | 1 | "One table or graph is highlighted as the best reflection of all the relevant gains and losses": the "What the model says" table on the landing page (`index.html`, the `table.scen` block), the four Table 3 rows that carry the gains and losses at the paper's three settings | Level 2 needs "a sample output published pre-release of final results". The format is the paper's, not this project's, and git history begins 2026-09-21, after the reproduction ran, so nothing timestamped precedes the first result. The landing page now says so (`477593d`). Also note that the table shows three scenario columns without naming one as preferred, which the paper itself does not do either |
| 2 | Input-output link | 3 | "An interactive tool allowing for adjusted inputs is provided, and its underlying code shares the same key sections of code behind the analysis section": `explorer/grid.js` (7 dials, 4374 cells) is written by `slides/make_grid_app.py`, which imports `aiscen.simulate` (lines 24-25), the code the report and tests run; `tests/test_explorer_grid.py` checks the grid against the exporter and the named corners against their scenarios, and CI (`.github/workflows/ci.yml`, first run pending) regenerates the grid and fails if it differs | None (top level) |
| 3 | Methodological accounts | 3 | "Code is clearly documented into a dynamic document": `repro.qmd` (Quarto, `code-fold: true`), every table and inline estimate computed from `aiscen/`; no spreadsheets | None (top level). An archival DOI (Zenodo) would make the "trusted repository" in levels 1-2 unambiguous |
| 4 | Data | 2 | "Analytic data is made available through a trusted repository": `slides/data/*.csv` and `out/` (the committed output of `run.py --survey --csv out`), both in the public GitHub repo. Raw inputs: `README.md` "Not reproducible without the authors' data" gives an access line per external source (CPS tables, IPUMS-CPS, the Carrillo-Tudela and Visschers replication files by DOI, JOLTS, BTOS, FRED); the survey microdata behind Tables 2 and 4 is unreleased, which is not applicable rather than absent | Level 3 needs "analytic and raw data ... through a trusted repository". The public raw series are linked but not bundled, and the calibration targets are transcribed into `aiscen/params.py` rather than recomputed from them. A script that fetches those series and recomputes the targets, with the pulled files hashed, would close it |
| 5 | Open report | 3 | "A final report in the form of a dynamic document or an open notebook, and include version control tracking": `repro.qmd`, rendered to `repro.html`, in git | None (top level) |
| 6 | File structure | 3 | Self-contained repo: `aiscen/` (model), `tests/`, `slides/`, `explorer/`, `out/`, `repro.qmd`, `Makefile`; `README.md` "Layout" maps every file | None (top level) |
| 7 | Label inputs | 3 | "List all inputs, their sources, and provide links or detailed references": `repro.html#every-input-by-origin` (source `repro.qmd`, the `origins` chunk; exported to `slides/data/inputs.csv`) lists 31 rows as data 9, research 8, guesswork 10, derived 2, convention 2 (the last two are this project's extensions), each with a basis and a paper page/table locator, URLs for data rows, and "Set by the authors, September 2026" on every guesswork row | None under the Guidelines' wording. Several research rows read "Table 1 cites X without a location": the paper names the source but no table or page, and this project has not looked them up |
| 8 | Reproducible code | 2 | "Code is easily readable and possible to run regardless of software dependencies": the model and exporters are standard-library Python; `make all` rebuilds tests, CSVs, report, grid and deck; `requirements.txt` lists the render dependencies; CI on a clean Ubuntu runner (`.github/workflows/ci.yml`, added `97e6e32`) runs the suite and the grid check (first run pending; this row does not depend on it) | Level 3 needs "possible to run with just one click": a Binder or Codespaces devcontainer. Unpinned `requirements.txt` and no Quarto/R in CI mean the report and deck renders are checked only locally |
| 9 | Version control | 3 | "Use version control software and track changes in a shared project repository": git, public at `github.com/fhoces/opa-ai-macro-econ-scenarios`, all work committed, `v1.0` tagged | None at this level. History begins 2026-09-21, eleven days after work began; the earlier work has no commit record |

**Vector (steps 1-9): 1 · 3 · 3 · 2 · 3 · 3 · 3 · 2 · 3. Headline level (minimum): 1.**

## Best credibility per unit of effort

1. **Step 8 to 3:** a `.devcontainer/` (or Binder `environment.yml`) so the tests and grid run
   in one click. Small, since the model needs only the standard library and pytest.
2. **Step 4 to 3:** a fetch-and-recompute script for the public calibration inputs (CPS
   tables, JOLTS, BTOS first; IPUMS needs registration and stays an instruction).
3. **Step 1:** cannot be raised retroactively for this reproduction. For the next edition
   of the paper, publish the intended headline table (with empty cells) in a dated commit
   before re-running it.
