# Reimplementation: "Economic Scenarios for Transformative AI"

<img src="assets/opa/opa-materials.png" align="right" width="130" alt="The materials layer of the Open Policy Analysis stack">

An independent, from-scratch implementation of the model in

> Korinek, Anton, Charles I. Jones, Szymon Sacher, Tess Cotter and Peter McCrory (2026),
> "Economic Scenarios for Transformative AI", The Anthropic Institute Working Paper
> No. 2026-02, September 2026.

Version 1.0, September 2026 (git tag `v1.0`). DOI: to be added once the release is archived.

The work is organised in three layers, adapted from the
[Open Policy Analysis](https://tinyurl.com/1qypbihb) (OPA) framework:

1. **Open Output**: [an interactive explorer](https://fhoces.github.io/opa-ai-macro-econ-scenarios/explorer/)
   over a precomputed grid of the paper's seven scenario dials: 4374 combinations, three
   levels per dial (six for reinstatement), each showing eleven outcomes in 2030 and the
   2025-2030 paths of three of them.
2. **Open Analysis**: [a full written reproduction](https://fhoces.github.io/opa-ai-macro-econ-scenarios/repro.html)
   that walks every table and equation in the paper's own order, and
   [a slide deck](https://fhoces.github.io/opa-ai-macro-econ-scenarios/slides/slides.html)
   that teaches the same material step by step.
3. **Open Materials**: this repository, which stores the `aiscen` model, its test suite,
   and every exported CSV needed to replicate the analysis in full.

Quick check: `python3 -m pytest -q` runs the 129 tests (Python 3.9+, standard library plus
pytest); the full commands are under [Usage](#usage).

[The landing page](https://fhoces.github.io/opa-ai-macro-econ-scenarios/) links to all
three. The deck pulls `remark.js` from a CDN and the report pulls MathJax from one, so both
need an internet connection to render fully; the explorer is self-contained apart from
web fonts.

To learn more about the OPA framework and BITSS, its home at UC Berkeley,
[click here](https://www.bitss.org/opa/).

### The paper itself is not in this repo

It is third-party content, so it is deliberately untracked (see `.gitignore`) rather than
redistributed here. Get it from the source:

- Landing page, with the scenario explorer and the version label:
  <https://www.anthropic.com/institute/econ-scenarios>
- PDF, 57 pages, linked from that page:
  <https://www-cdn.anthropic.com/files/4zrzovbb/website/cf58f84d46a4a76bf5a5b039ac695fba6b80041c.pdf>
  (both checked 2026-09-21)

Save it as `paper.pdf` in this directory if you want the local copy the page references in
this README and in `repro.qmd` point at. Nothing in the code reads it; it is needed only for
reading along. The landing page called itself **Version 1.0** when this reproduction was
written, so if a later version appears, the page and equation numbers cited throughout may
have moved.

**No replication package was published with the paper** (searched 2026-09-10: the PDF
carries no data or code availability statement, and there is nothing on GitHub, Hugging
Face, Zenodo, OSF, RePEc, or the authors' pages). The only public implementation is the
minified client-side bundle behind the scenario explorer at
`anthropic.com/institute/econ-scenarios`. Everything here is written from the equations
printed in the paper: Proposition 1 (p. 15), the closed form for a frictionless economy
where labor reallocates instantly; the 44-equation monthly system of Table A.1
(pp. 42-43); the simulation procedure of Appendix A (pp. 40-41); the innovation block of
Appendix C (pp. 49-51); and the parameters of Tables 1 and A.2 (pp. 23-25, 43-45).

**A note on terminology.** The paper calls the occupations whose tasks AI is assumed to
touch "cognitive". This README, the deck, the explorer and the landing page call them
**AI-sensitive** instead, because the paper's label implies the excluded work (the electrician's,
the home health aide's) involves no thinking. The subscript `C` in the math, the `aiscen` code
and the CSV row names keep the paper's wording, so the data still lines up row for row
with the paper; `repro.qmd`, which follows the paper line by line, keeps it too and says so.

## Status: the paper's published tables reproduce

| Published table | Cells | Result |
|---|---|---|
| Table 3, the three scenarios in 2030 (p. 31) | 20 rows x 4 columns (80 cells, including the No-AI baseline column) | within test tolerance on every cell; two need a widened tolerance and seven round to a different printed digit (below) |
| Table 5, four elasticities of capital supply (p. 37) | 5 rows x 8 columns (40 cells) | within test tolerance on every cell, including the pegged-rental case eps = infinity; one cell rounds to a different printed digit (below) |
| Table 6, four rigidities of the AI-sensitive wage (p. 38) | 7 rows x 7 columns (49 cells) | within test tolerance on every cell; eight cells round to a different printed digit (below) |

Independent checks the paper states in prose and that the code hits without being
targeted at them: the steady-state cross-group switching share of 1/7 (p. 21), the
monthly filling rates 0.66 and 0.64 with matching efficiency chi = 0.76 (p. 21; the
second rate is 0.635 at Table 1's pool and 0.64 at 0.0384, see below), the
aggregate finding rate 0.23 (p. 26), the logistic slopes kappa_m = 0.33 and
kappa_d = 0.51 (Table A.2, p. 45), the research share going from 3.5 to 4.1 percent of GDP
(p. 50), the worked example in Section 2.1.3 where the TFP gain is 0.032 to first order
and 0.029 exactly (p. 12), the claim that the monthly ideas step stays within
0.02 percentage points of the closed form (p. 41), and footnote 14's mixed run (p. 37:
the substantial scenario's m, d and a, the extreme scenario's psi, mu and rho, and eps = 1), where GDP ends 7.2 percent
above the no-AI path (7.21 here) while labor income falls by 4.3 percent of no-AI GDP
(4.31 here). The same footnote's third figure does not reproduce: holding the AI-sensitive
occupations' income at its no-AI level takes a transfer of 84 percent of the GDP gain in
the paper and 87 percent here (83 percent if posting speed is also set to the extreme
scenario's 0.5, which the footnote does not say).

One further cross-check, of the model against itself by a different route: the measured
TFP index (45) is compared with its dual (25), the chained share-weighted growth of the
wage and the rental rate, integrated from the no-AI baseline. Appendix C.4 says the two
agree only to first order, and they do: the two indices differ by 0.001 percentage points
in the modest scenario and part company as the shock grows (0.09, 1.9 and 7.1 percent of
the gap in the three scenarios), which is how a base-weighted and a chained index should
behave. This validates the wage, rental-rate and labor-share paths against the TFP path
independently of the published tables.

**Where the printed digit differs.** The three tables hold 169 cells between them.
Every one is inside the test suite's numerical tolerance, and 153 of them also round to
the digit the paper prints. These 16 do not. None is off by more than 0.11 percentage
points, and two are the same model run reported in two tables (the baseline is
`xi = 0.5`, `eps = 3`), so there are 14 distinct results here.
`tests/test_printed_precision.py` carries this list as an exact allowlist, rounding
half-up to the paper's own number of decimals, so a cell moving in or out of agreement
fails the suite rather than quietly ageing the text.

| Table | Cell | Reproduced | Published |
|---|---|---|---|
| Table 3 | modest, GDP index 2024 = 100 | 114.56 | 114.5 |
| Table 3 | extreme, GDP growth pct per year | 15.46 | 15.4 |
| Table 3 | extreme, AI-sensitive employment since mid-2026 | -21.44 | -21.5 |
| Table 3 | No AI, unemployment rate AI-sensitive | 2.82 | 2.9 |
| Table 3 | substantial, unemployment rate all workers | 4.53 | 4.6 |
| Table 3 | substantial, growth of the ideas stock | 1.767 | 1.76 |
| Table 3 | extreme, growth of the ideas stock | 2.027 | 2.02 |
| Table 5 | substantial, eps=6, GDP above no-AI | 9.05 | 9.1 |
| Table 6 | substantial, xi=0.5, unemployment all workers | 4.53 | 4.6 |
| Table 6 | substantial, xi=0.75, unemployment AI-sensitive | 5.03 | 5.1 |
| Table 6 | substantial, xi=0.9, unemployment all workers | 5.12 | 5.2 |
| Table 6 | extreme, xi=0, AI-sensitive wage w_C | -42.09 | -42.2 |
| Table 6 | extreme, xi=0.5, AI-sensitive employment | -21.44 | -21.5 |
| Table 6 | extreme, xi=0.75, AI-sensitive employment | -25.83 | -25.9 |
| Table 6 | extreme, xi=0.75, unemployment AI-sensitive | 21.65 | 21.7 |
| Table 6 | extreme, xi=0.9, unemployment all workers | 15.12 | 15.2 |

**The pool rounding accounts for six of them.** Table 1 gives the normal search pool
as `U_bar = 0.038`, but the quit-rate derivation on p. 26 uses 3.84 percent and the
published pool split of 1.76 / 2.08 percent (p. 21) requires 0.0384. At
`Fixed(U_bar=0.0384)` seven of the sixteen cells above land on the published digit: six
unemployment cells, including every all-workers one, which the pool explains, and Table 5's
substantial eps=6 GDP cell, which moves by 0.006 and crosses its rounding boundary by
coincidence. The same fork moves the p. 21 filling rate for the all-other group from
0.635 to 0.64. Nothing else changes materially. The
No-AI AI-sensitive rate is the near miss: it improves from 2.82 to 2.85, which still prints
as 2.8 rather than the paper's 2.9, so the pool accounts for the size of that gap
without closing it. Those same two Table 3 cells, all workers in the substantial column
(4.53 against 4.6, a 0.07pp gap) and AI-sensitive in the No-AI column (2.82 against 2.9, a
0.08pp gap), are also the only two Table 3 cells outside that table's standard tolerance (0.05
points for values below 10, 0.10 at or above), which is why `tests/test_table3.py` widens it, to 0.09 points, for exactly
those two. They are not unusually far off: twelve other cells of the 169 also sit more than 0.05
points from the printed figure, three of them Table 3 values above 10 and the rest in
Tables 5 and 6, which are tested against a looser floor of 0.12 points; among them the
same rounding leaves four Table 6 unemployment cells 0.07
to 0.08 points low (one of them, substantial `xi = 0.5` all workers, is the identical model
run). The
default here stays at Table 1's 0.038 for transcription fidelity; the tests check both
readings.

**The other eight are last-digit noise.** Leaving aside the No-AI rate above, the cells
still off sit between 0.0065 and 0.11 percentage points of the published figure at the
default pool (the largest, the extreme `xi = 0` AI-sensitive wage, widens to 0.13 at
0.0384),
share no common cause (two of them are one model run reported in Table 3 and Table 6),
and every one passes the test
suite's numerical tolerance (`max(0.12, 0.004 * |published value|)` percentage points
for Tables 5 and 6, in `tests/test_robustness.py`). That is what ordinary rounding in a
nonlinear numerical solve looks like rather than a modelling discrepancy, but
"reproduced to the printed precision" overstated it, and the table above is the
accurate claim.

## Where the inputs come from

Table 1 of the paper gives a source for each number in a prose column. The report
re-sorts the same information by how much evidence stands behind each input, in
[Every input, by origin](https://fhoces.github.io/opa-ai-macro-econ-scenarios/repro.html#every-input-by-origin),
using the three labels of the Open Policy Analysis guidelines: **data** (read off a
public dataset), **research** (an estimate from a published paper, or a received
conventional value) and **guesswork** (set by assumption, however well bounded). Of the
31 rows, 9 are data, 8 research, 10 guesswork, 2 derived from other rows and 2 dates or
grid conventions.

The headline: **all seven scenario dials are guesswork**, and they are exactly what
differs between modest, substantial and extreme, so they produce the entire spread in
the results. Apart from the gain's mid-2026 anchor, which also differs by scenario, and two
further assumptions (the returns to research `lambda` and labor-force growth `n`),
everything they are measured against is data or research. The normal-times
labor market in particular is pinned hard (the search pool, the quit rate, the
separation rates by group, the occupational switching matrix and the filling rate are
all data). This is not a criticism of the calibration, it is what a scenario exercise
is, but it means the results are a map from seven guesses to outcomes rather than a
forecast. The [scenario explorer](https://fhoces.github.io/opa-ai-macro-econ-scenarios/explorer/)
is that map, made clickable.

## Not reproducible without the authors' data

* **Table 2** (the five parameters implied by the survey) and **Table 4** (the economies
  the survey answers imply): these need the respondent-level answers of the Morning
  Consult survey of 10,980 US adults fielded 11-23 August 2026, which has not been
  released. Table 4 reports medians *of outcomes across respondents*, which is not the
  same as the outcome at the median answers, so it cannot be recovered from the published
  medians. `SURVEY_MEDIAN` in `aiscen/params.py` runs the model at Table 2's median
  parameters as an indicative comparison only (it gives GDP 9.9 percent above the no-AI
  path against Table 4's median of 8.6).
* **Figure 1** (the capability question by task) is survey output.
* The paper's external inputs are public but not bundled here. The calibration targets
  they produce are transcribed as numbers in `aiscen/params.py` rather than recomputed
  from source. Where each one lives:
  * **CPS 2025 annual averages** (`cog_share`, the two groups' employment shares, and
    `U_bar`, the unemployed pool): BLS, Labor Force Statistics from the CPS, Household
    Data Annual Averages 2025, Table 11 (employed people by detailed occupation) and
    Table 25b (unemployment by detailed occupation), at [bls.gov/cps](https://www.bls.gov/cps/).
  * **IPUMS-CPS matched monthly files 2010-19** (the finding rate behind `q_bar_ann`, and
    the separation rates by group, `q_rel_C` and `q_rel_N`): the basic monthly samples with
    the month-to-month linking keys, from [cps.ipums.org](https://cps.ipums.org/cps/)
    (free registration); the paper cites Flood et al. (2025).
  * **The occupational switching matrix** (`mu_bar`): tabulated from the replication files
    of Carrillo-Tudela and Visschers (2023), "Unemployment and Endogenous Reallocation over
    the Business Cycle", Econometrica 91(3), which are the article's supplementary material
    at the Econometric Society, DOI [10.3982/ECTA12498](https://doi.org/10.3982/ECTA12498).
  * **JOLTS** (the quits elasticity `q_resp_share` and the 2010-19 filling rate
    `fill_bar`): [bls.gov/jlt](https://www.bls.gov/jlt/); the paper takes the quits rate
    series JTSQUR from [FRED](https://fred.stlouisfed.org/).
  * **Census BTOS AI supplement** (`d_anchor`, the mid-2026 diffusion share): the AI use
    estimates and the 2026 supplement at [census.gov/hfp/btos](https://www.census.gov/hfp/btos/).
  * **FRED** (the CPS unemployment levels UNEMPLOY and UEMPLT5 in the paper's references):
    [fred.stlouisfed.org](https://fred.stlouisfed.org/).

## Usage

`make test`, `make csv`, `make report`, `make grid`, `make slides` (or `make all`) run the
commands below; the `Makefile` reads `QUARTO_PYTHON` and `RSTUDIO_PANDOC` from the
environment and falls back to the `python3` and `pandoc` on your PATH. The explicit form:

```sh
python3 run.py                      # print the Table 3 / 5 / 6 comparisons
python3 run.py --survey --csv out   # add the survey-median run, write paths and comparison CSVs
python3 -m pytest -q                # 129 tests: the checks above, the explorer grid, the slop extension, the typed-in prose numbers

# the narrative report: every table and inline estimate, in the paper's own order
QUARTO_PYTHON=/opt/anaconda3/bin/python3 quarto render repro.qmd

# the scenario explorer's precomputed grid (writes explorer/grid.js, ~30s)
python3 slides/make_grid_app.py

# the slide deck
cd slides && RSTUDIO_PANDOC=/Applications/quarto/bin/tools/aarch64 \
  Rscript -e 'rmarkdown::render("slides.Rmd", quiet=TRUE)'
```

`repro.qmd` walks the paper section by section, from the production function through
the calibration to the results and the two robustness tables, computing each figure
the text quotes inline rather than restating it. Rendering it is itself a check: a
failed chunk aborts the render, and every published number appears next to the
reproduced one. It needs pandas, matplotlib and tabulate on top of the package's
standard-library-only core (see `requirements.txt`), and the `QUARTO_PYTHON`
override points Quarto at the interpreter that has them.

`QUARTO_PYTHON=/opt/anaconda3/bin/python3` and
`RSTUDIO_PANDOC=/Applications/quarto/bin/tools/aarch64` above are this machine's own
paths, not portable constants: point `QUARTO_PYTHON` at wherever your `python3` with
pandas/matplotlib/tabulate installed actually lives, and `RSTUDIO_PANDOC` at the
`pandoc` binary bundled with your own Quarto or RStudio install (`quarto --version`
and `quarto pandoc --version`, or `which pandoc`, will locate it).

The package itself requires Python 3.9+ and the standard library only (`pytest` for the tests). No numpy or
scipy dependency: every root-find (the rental-rate gap, the price index, and the
steady-state pool split and matching efficiency) is a bisection in `aiscen/numerics.py`.

```python
from aiscen import Fixed, SCENARIOS, simulate
res = simulate.run(Fixed(), SCENARIOS["extreme"])
m = res.at(2030.0)          # every variable of Table A.1, that month
res.series("u_rate")        # monthly path of any field
```

## Layout

| File | Contents |
|---|---|
| `aiscen/params.py` | Tables 1 and A.2: fixed parameters, the three scenarios, the survey medians, and `gain_path`, the explorer's straight-line gain convention |
| `aiscen/paths.py` | Equations (8) and (8'): the logistic paths for m and d, the linear gain a |
| `aiscen/steady.py` | Equation (38), Table A.1 panel E: the normal-times search steady state |
| `aiscen/statics.py` | Proposition 1 (exact closed form) and the actual-economy system (39) |
| `aiscen/simulate.py` | Appendix A steps 1-9 on a monthly grid, plus the closed form (43) |
| `aiscen/report.py` | Table 3 rows, the published Tables 3, 5 and 6, and the comparison printout |
| `aiscen/numerics.py` | The bisection routine behind every root-find |
| `aiscen/slop.py` | The exploratory "AI slop" extension; outside the reproduction, its mechanism pinned by four tests |
| `tests/` | The validation suite: paths, steady state, statics, Table 3, Tables 5-6, identities, and `test_prose_numbers.py`, which recomputes the numbers typed into the explorer page and the deck |
| `repro.qmd`, `repro.css` | The narrative report: the paper's sections in order, every equation explained, tables and inline estimates computed |
| `slides/` | The xaringan deck walking through the paper in four parts: the claim, the model, solving it for US inputs, results (see `slides/README.md`) |
| `repro.html` | The rendered report. Committed, not ignored, because Pages serves it |
| `explorer/` | The scenario explorer: `index.html` plus the precomputed `grid.js`, also committed for Pages |
| `index.html`, `.nojekyll` | The Pages landing page, and the marker that stops Jekyll eating `slides_files/` |
| `coverage.md`, `coverage.html` | Reception of the paper: press, commentary, revisions. Linked from the landing page; the `.md` is the source and `render_understanding.py` rebuilds the `.html` |
| `run.py` | Command-line comparison tables, and with `--csv` the monthly paths plus `table3/5/6.csv` and `slop.csv` |
| `out/` | The committed output of `python3 run.py --survey --csv out` |
| `requirements.txt`, `pytest.ini` | Rendering dependencies for the report, and the test configuration |
| `Makefile` | `make test / csv / report / grid / slides / all`: the Usage commands, with the two tool paths taken from the environment |
| `.github/workflows/ci.yml` | Continuous integration: on every push to `main`, every pull request, and on demand, a clean Ubuntu machine with Python 3.11 installs pytest, runs the test suite, then regenerates `explorer/grid.js` and fails if it differs from the committed file |
| `CREDIT.md`, `credit-answers.json` | Who did what, by CRediT contributor role, for each of the five objects; the `.json` holds the raw questionnaire answers the page and the landing-page table are built from |
| `AUDIT.md` | A self-audit against the BITSS Open Policy Analysis guidelines: each of the nine steps, the level it reaches, the evidence, and what the next level needs |
| `assets/opa/` | The four Open Policy Analysis layer images used on the landing page, the explorer, the report, the deck and this README |
| `LICENSE` | MIT License |

## Readings the paper leaves implicit

Readings 1 to 4 were resolved by requiring internal consistency and are each checked by a
test; 5 and 6 are documented choices, exposed as switches. They are the places where a different reader might reasonably code something else.

1. **Equation (13) with endogenous ideas.** As printed, `ell_N_tilde = dln(Y/L) -
   sigma dln w`, which acquires a spurious `(1 - sigma) dln A` term once the ideas stock
   moves. Equation (15), the exact row Table A.1 actually uses, has no ideas term, and
   labor demand for the unaffected group derived from scratch gives
   `dln(Y/L) - sigma dln w - (1 - sigma) dln A`. The code uses (15).
2. **A-deflation in system (39).** The note to Table A.1 says the wages in (39) are
   deflated by `A_t`. Consistency with Proposition 1 requires the output gap in the two
   labour-demand rows to be deflated as well; the capital row then pins the deflated gap
   in closed form as `(eps + sigma) dln r - ln(B / s_K0) - dln A`. The test
   `test_system_39_at_the_targets_is_proposition_1` enforces the paper's own statement
   that (39) at the targets *is* Proposition 1, with and without an ideas gap.
3. **Which AI-sensitive wage prices the economy.** Step 8 of Appendix A evaluates (39)
   "at realized employment", which prices AI-sensitive labor at the marginal product
   consistent with that employment, and then reports "the cognitive wage paid"; the
   Table A.1 note says the price in (39) is the sticky wage, "or MPL_C where employment
   trails demand". Both are computed (`dlnw_C_mpl`, `dlnw_C_paid`); the
   published `w_C` row of Table 3 matches the wage *paid*, which is what the comparison
   uses. The gap between them is the profit of the firms employing AI-sensitive
   occupations, which the paper bounds at half a percent of GDP.
4. **Reporting conventions.** Level differences in Tables 3, 5 and 6 are percent
   deviations, `exp(dln x) - 1`, not log points; growth rates are log changes over the
   preceding twelve months (note to Table 3). Reading the extreme scenario's GDP gap as
   log points, for instance, gives 28.1 rather than the published 32.4.
5. **The gain path for a survey-style run.** `a_t` is linear from a mid-2026 anchor, and
   the anchor is itself a scenario assumption (0.30 / 0.35 / 0.45). For a run set from
   2030 answers the paper does not say which anchor to use; `scenario_from_2030_values`
   takes the substantial scenario's 0.35, consistent with the Table 4 note that
   unasked parameters stay at that scenario's values.
6. **Rate conventions.** Appendix A converts per-period fractions to continuously
   compounded rates (`q = -ln(1 - q_hat)`); `Fixed(cc_rates=False)` switches that off and
   moves nothing visible in the published tables.

## License

The code, report, slide deck, explorer and exported CSVs in this repository are released
under the [MIT License](LICENSE). That license covers only the work done here: writing the
model out in code, testing it, and explaining it.

It does **not** cover the underlying analysis, which belongs to its authors. The model,
its equations, the scenario design, the parameter values and the published results are
those of Korinek, Jones, Sacher, Cotter and McCrory (2026), cited at the top of this
README; they are restated here only so the reproduction can be checked against them, and
nothing in this repository claims them as original. If you use this code, please cite
that paper for the analysis. The paper itself is not redistributed (see above), and the
external data inputs listed under [Where the inputs come from](#where-the-inputs-come-from)
remain under their publishers' terms.

<sub>OPA done by [Fernando Hoces de la Guardia](https://fhoces.github.io)</sub>
