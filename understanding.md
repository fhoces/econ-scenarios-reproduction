# Understanding tracker: Korinek, Jones, Sacher, Cotter and McCrory (2026)

A running record of which parts of this material I claim to understand, so that a later
session can test me on the parts marked solid and teach the parts that are not.

Scope: the deck (`slides/slides.Rmd`, 80 slides), the reproduction report
(`repro.qmd` / `repro.html`), and the Python package (`aiscen/`).

Statuses are **self-claimed and untested** until a test happens. Test results go in the
log at the bottom, and a failed question moves the row back a level.

## How to use this file

- Say **"test me on X"** and questions are drawn only from rows marked Solid or Nearly.
  Rows below that get explained, not examined.
- Say **"test me"** with no topic and the questions are spread across every Solid row,
  weighted toward the ones tested least recently.
- After a test, the status column is updated with the date and the log records what was
  missed, so the next test can retry exactly those points.

## Status legend

| Mark | Meaning |
|---|---|
| **Solid** | I can state it, explain why it holds, and answer follow-ups without the slides |
| **Nearly** | The structure is there; some steps still need the slide in front of me |
| **Partial** | I follow the narrative but could not reconstruct it |
| **Not yet** | Not worked through |
| **Skipping** | Deliberately out of scope for now |

## Where the parts are

The deck was restructured on 2026-09-21: the derivation part moved ahead of the solving
part, so the numbering below is **not** the numbering this file used before that date.

| Part | Slides |
|---|---|
| 1. The claim | 3-17 |
| 2. The model, equation by equation | 18-33 |
| 3. Solving the model for US inputs | 34-47 |
| 4. Results: some scenarios and the explorer | 48-60 |
| Backups | 61-80 |

---

## Part 1: the claim (3-17)

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| The main claims of the model | **Solid** | 5-7 | The three scenarios and what separates them; GDP 1.6 / 8.3 / 32.4 percent above the no-AI path by 2030 and why the wage split matters more than the level; that these are gaps against a counterfactual, not forecasts |
| What the paper is doing (the mapping exercise) | **Solid** | 4, 7, 17 | That it maps assumptions to consequences rather than estimating anything; which quantities are assumed and which are derived; why "scenario" is not "prediction" |
| The seven inputs | **Solid** | 8-15, 17 | Name all seven (m, d, a, psi, rho, mu, theta_H), say what each does to the economy, which are anchored to data and which are assumptions, and the direction each moves wages and unemployment |
| Terminology: AI-sensitive vs the paper's wording | **Solid** | 4 | Why the deck renames the occupation group and what is unchanged underneath |
| The model on one page | **Solid** | 17 | The three blocks: fixed empirical inputs against the seven assumed ones, the single optimizing agent plus the frictions, and the eleven reported series |

## Part 2: the model, equation by equation (18-33)

**Not claimed.** This is the one part still open, and it is the part that derives every
equation the other parts use.

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| Task-based production, and the assignment rule | Not yet | 19-21 | Why (1) and (2) are not an aggregate production function, and what (3) decides |
| Prices, shares, and why sigma < 1 carries the result | Not yet | 22 | |
| TFP: Hulten and Domar weights | Not yet | 23 | |
| The factor-price frontier and capital supply | Not yet | 24-25 | |
| The labor share, three channels | Not yet | 26 | |
| Employment and the targets | Not yet | 27 | |
| Proposition 1 | Not yet | 28 | |
| Growth vs levels | Not yet | 29-30 | |
| Unemployment and matching | Not yet | 31-32 | |
| What Part 2 produced | Not yet | 33 | The closed equation set, and that only (18) and (39) are implicit |

## Part 3: solving the model for US inputs (34-47)

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| The whole machine, with the numbers | **Solid** | 35 | Which inputs are measured and fixed, which are assumed, what runs once, what runs monthly |
| Calibration: where the numbers come from | **Solid** | 36 | Which rows are constants, which are anchors, which are ranges, and why none is one of the seven |
| Step 0: the steady state, equation (38) | **Solid** | 37-38, 61-63 | What goes in, what comes out, why no scenario input may enter, and that it needs two root-finds (U-bar_C and chi) |
| The month in nine steps | **Solid** | 39, 42-45 | Recite Appendix A's steps 1 to 9 and say why each can only run after the one before |
| The 44 equations and the solve order | **Solid** | 40-41, 65 | Why the month is a sequence rather than a simultaneous system |
| Reading prices off quantities, system (39) | **Solid** | 46 | Why the demand system is inverted; that (39) is three rows, not one; where it fires twice in the month |
| The root-finds | **Solid** | 47, 63, 67 | Four per month, all one-dimensional in Delta ln r: (18) once, (39) three times; the residual and bracket for each |

## Part 4: results, and the explorer (48-60)

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| The eleven reported series, and which are plotted | **Solid** | 49 | What the model reports, and that these pictures show four of the eleven |
| The three scenarios, one at a time | **Solid** | 50-52 | For each: the seven inputs, the 2030 outcomes, and the channel that drives them |
| The robustness tables | **Solid** | 53 | Why epsilon and xi are the two the paper varies, and what each trades off |
| The survey | **Solid** | 54 | What was asked, and why the median answers land near the substantial scenario |
| What reproduces, and what does not | **Solid** | 55-56, 73 | Which published tables match to printed precision, and the U-bar rounding fork |
| Takeaways and the first postscript | **Solid** | 57-58 | The three labels against the seven inputs, and where the named scenarios sit in the grid |
| The AI-slop extension (second postscript) | **Solid** | 59-60, 72 | Why slop is a distributional event rather than a missing boom, and why the wage sign flips |

## The reproduction itself

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| What the reproduction establishes | **Solid** | 55, `repro.qmd` | Which published tables are matched and to what precision |
| The one number that does not reproduce | **Solid** | 73, `repro.qmd` | The U-bar rounding fork, and why it is a fork rather than an error |
| The code layout | Not yet | `aiscen/` | Which file holds the steady state, the monthly loop, the statics, the scenarios |

---

## Question formats a test may use

1. **State it.** Define a symbol or name the seven inputs, from memory.
2. **Trace it.** Given a step, say what must already be known and what it produces.
3. **Move a dial.** Raise one input, predict the sign of the move in GDP, the two wages
   and unemployment, and say through which equation.
4. **Spot the error.** A claim that is wrong in one specific way; find it.
5. **Read the number.** Given a figure or table from the deck, say what it does and does
   not license you to conclude.

## Log

- **2026-09-17.** Tracker created. Claimed at the start: the claim, the mapping exercise
  and the seven inputs Solid; the solving part Nearly; everything else Not yet.
- **2026-09-21.** Deck restructured, so the part numbering here changed: the derivation
  part is now Part 2 and the solving part is now Part 3. Claimed today: **Parts 1, 3 and 4
  Solid**, which promotes the whole solving part from Nearly and all of Part 4 from Not
  yet. Part 2, the derivation, is now the only part not claimed. Still nothing tested.
  The first test should start with the five things asked about while building the deck,
  all of which now sit inside claimed ground: what f_C and f_N are, why the Proposition 1
  collapse check validates system (39), the difference between capital demanded and
  supplied, why there is a bisection every month and how many, and what the 39 in
  "system (39)" refers to.
