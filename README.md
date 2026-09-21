# Reimplementation: "Economic Scenarios for Transformative AI"

An independent, from-scratch implementation of the model in

> Korinek, Anton, Charles I. Jones, Szymon Sacher, Tess Cotter and Peter McCrory (2026),
> "Economic Scenarios for Transformative AI", The Anthropic Institute Working Paper
> No. 2026-02, September 2026.

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
printed in the paper: Proposition 1 (p. 15), the 44-equation monthly system of Table A.1
(pp. 42-43), the simulation procedure of Appendix A (pp. 40-41), the innovation block of
Appendix C (pp. 49-51), and the parameters of Tables 1 and A.2 (pp. 23-25, 43-45).

## Status: the paper's published tables reproduce

| Published table | Cells | Result |
|---|---|---|
| Table 3, the three scenarios in 2030 (p. 31) | 20 rows x 3 scenarios | reproduced to the printed precision, except one row (below) |
| Table 5, four elasticities of capital supply (p. 37) | 5 rows x 8 columns | all cells reproduced, including the pegged-rental case eps = infinity |
| Table 6, four rigidities of the cognitive wage (p. 38) | 7 rows x 7 columns | all cells reproduced |

Independent checks the paper states in prose and that the code hits without being
targeted at them: the steady-state cross-group switching share of 1/7 (p. 21), the
monthly filling rates 0.66 and 0.64 with matching efficiency chi = 0.76 (p. 21), the
aggregate finding rate 0.23 (p. 26), the logistic slopes kappa_m = 0.33 and
kappa_d = 0.51 (p. 48), the research share going from 3.5 to 4.1 percent of GDP
(p. 50), the worked example in Section 2.1.3 where the TFP gain is 0.032 to first order
and 0.029 exactly (p. 12), and the claim that the monthly ideas step stays within
0.02 percentage points of the closed form (p. 41).

One further cross-check, of the model against itself by a different route: the measured
TFP index (45) is compared with its dual (25), the chained share-weighted growth of the
wage and the rental rate, integrated from the no-AI baseline. Appendix C.4 says the two
agree only to first order, and they do: the two indices differ by 0.001 percentage points
in the modest scenario and part company as the shock grows (0.09, 1.9 and 7.1 percent of
the gap in the three scenarios), which is how a base-weighted and a chained index should
behave. This validates the wage, rental-rate and labor-share paths against the TFP path
independently of the published tables.

**The one discrepancy.** The all-workers unemployment rate comes out about 0.07
percentage points below the published figure in every scenario (e.g. 4.53 against 4.6 in
the substantial scenario). Table 1 gives the normal search pool as `U_bar = 0.038`, but
the quit-rate derivation on p. 26 uses 3.84 percent and the published pool split of
1.76 / 2.08 percent (p. 21) requires 0.0384. At `Fixed(U_bar=0.0384)` that row lands on
the published values exactly and nothing else changes materially. The default here stays
at Table 1's 0.038 for transcription fidelity; the tests check both.

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
* The paper's external inputs are public but not bundled here: IPUMS-CPS matched monthly
  files 2010-19, the Carrillo-Tudela and Visschers (2023) Econometrica replication files
  for the occupational switching matrix, CPS 2025 annual averages, JOLTS, the Census BTOS
  AI supplement, and FRED. The calibration targets they produce are transcribed as
  numbers in `aiscen/params.py` rather than recomputed from source.

## Usage

```sh
python3 run.py                      # print the Table 3 / 5 / 6 comparisons
python3 run.py --survey --csv out   # add the survey-median run, write monthly paths
python3 -m pytest -q                # 98 tests, all of the checks described above

# the narrative report: every table and inline estimate, in the paper's own order
QUARTO_PYTHON=/opt/anaconda3/bin/python3 quarto render repro.qmd
```

`repro.qmd` walks the paper section by section, from the production function through
the calibration to the results and the two robustness tables, computing each figure
the text quotes inline rather than restating it. Rendering it is itself a check: a
failed chunk aborts the render, and every published number appears next to the
reproduced one. It needs pandas, matplotlib and tabulate on top of the package's
standard-library-only core, and the `QUARTO_PYTHON` override points Quarto at the
interpreter that has them.

The package itself requires Python 3.9+ and the standard library only (`pytest` for the tests). No numpy or
scipy dependency: the two root-finding problems, the rental-rate gap and the price index,
are solved by bisection in `aiscen/numerics.py`.

```python
from aiscen import Fixed, SCENARIOS, simulate
res = simulate.run(Fixed(), SCENARIOS["extreme"])
m = res.at(2030.0)          # every variable of Table A.1, that month
res.series("u_rate")        # monthly path of any field
```

## Layout

| File | Contents |
|---|---|
| `aiscen/params.py` | Tables 1 and A.2: fixed parameters, the three scenarios, the survey medians |
| `aiscen/paths.py` | Equations (8) and (8'): the logistic paths for m and d, the linear gain a |
| `aiscen/steady.py` | Equation (38), Table A.1 panel E: the normal-times search steady state |
| `aiscen/statics.py` | Proposition 1 (exact closed form) and the actual-economy system (39) |
| `aiscen/simulate.py` | Appendix A steps 1-9 on a monthly grid, plus the closed form (43) |
| `aiscen/report.py` | Table 3 rows, the published values, and the comparison printout |
| `tests/` | The validation suite: paths, steady state, statics, Table 3, Tables 5-6, identities |
| `repro.qmd`, `repro.css` | The narrative report: the paper's sections in order, every equation explained, tables and inline estimates computed |
| `slides/` | A 46-slide xaringan deck walking through the paper: claim, theory, methods, results (see `slides/README.md`) |
| `repro.html` | The rendered report |
| `run.py` | Command-line comparison tables and monthly CSV export |

## Readings the paper leaves implicit

Each of these was resolved by requiring internal consistency, and each is checked by a
test. They are the places where a different reader might reasonably code something else.

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
3. **Which cognitive wage prices the economy.** Step 8 of Appendix A records the actual
   economy from (39) "at realized employment", which implies the cognitive price is the
   marginal product consistent with realized employment; the note also says the reported
   wage is the sticky wage paid. Both are computed (`dlnw_C_mpl`, `dlnw_C_paid`); the
   published `w_C` row of Table 3 matches the wage *paid*, which is what the comparison
   uses. The gap between them is the cognitive-firm profit the paper bounds at half a
   percent of GDP.
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
