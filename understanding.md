# Understanding tracker: Korinek, Jones, Sacher, Cotter and McCrory (2026)

A running record of which parts of this material I claim to understand, so that a later
session can test me on the parts marked solid and teach the parts that are not.

Scope: the deck (`slides/slides.Rmd`, 75 slides), the reproduction report
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

---

## Part 1: the claim (slides 3-16)

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| The main claims of the model | **Solid** | 5-7 | The three scenarios and what separates them; GDP 1.6 / 8.3 / 32.4 percent above the no-AI path by 2030 and why the wage split matters more than the level; that these are gaps against a counterfactual, not forecasts of growth |
| What the paper is doing (the mapping exercise) | **Solid** | 4, 7, 18, 57 | That it maps assumptions to consequences rather than estimating anything; which quantities are assumed and which are derived; why "scenario" is not "prediction" |
| The seven inputs | **Solid** | 8-15, 19 | Name all seven (m, d, a, psi, rho, mu, theta_H), say what each one does to the economy, which are anchored to data and which are assumptions, and which direction each moves wages and unemployment |
| Terminology: AI-sensitive vs the paper's wording | **Solid** | 4 | Why the deck renames the occupation group and what is unchanged underneath |
| Two ways to read the rest | Partial | 16 | The deck's own roadmap: solved-vs-derived |

## Part 2: how the model is solved (slides 17-30)

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| The shape of the whole thing | **Nearly** | 18 | Inputs, the once-only steady state, the 73 monthly solves, the outputs; which eight variables carry over from month to month |
| Calibration: where the numbers come from | **Nearly** | 19 | Which rows are constants, which are anchors, which are ranges, and why none of them is one of the seven inputs |
| The month, in nine steps | **Nearly** | 20, 25-28 | Recite the order and say why each step can only run after the one before it |
| Step 0: the steady state, equation (38) | **Nearly** | 21-22, 60 | What goes in (six calibrated constants), what comes out (nine objects), and why none of the seven inputs may enter |
| The 44 equations and the solve order | **Nearly** | 23-24, 65 | Why the month is a sequence and not a simultaneous system; where the only two root-finds are |
| Reading prices off quantities, system (39) | **Nearly** | 29 | Why the demand system is inverted; that the price index row plus two labor demands plus capital supply pin three price changes; how it reduces to one monotone equation in the rental rate |
| Why only two root-finds | **Nearly** | 30 | Monotonicity, bisection, no solver library needed |

Open snag in this part: **f_C and f_N** (job-finding rates by worker origin, slides 18, 21,
27). Asked about twice on 2026-09-17, now glossed on slide 18. Worth a question in the
first test.

## Part 3: where the equations come from (slides 31-45)

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| Task-based production | Not yet | 32-33 | |
| The assignment rule and the automation fork | Not yet | 34, 66 | |
| Prices, shares, and why sigma < 1 carries the result | Not yet | 35, 67 | |
| TFP: Hulten and Domar weights | Not yet | 36 | |
| The factor-price frontier and capital supply | Not yet | 37-38 | |
| The labor share, three channels | Not yet | 39, 68 | |
| Proposition 1 | Not yet | 40-41, 69-70 | |
| Growth vs levels | Not yet | 42-43, 74 | |
| Unemployment and matching | Not yet | 44-45, 71 | |

## Part 4: results and what to trust (slides 46-57)

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| The three scenarios, one at a time | Not yet | 47-49 | |
| The robustness tables | Not yet | 50 | |
| The AI-slop extension | Not yet | 51-52, 72 | |
| The survey | Not yet | 53 | |
| What reproduces, and what does not | Not yet | 54-55, 73 | |
| Takeaways | Not yet | 56-57 | |

## The reproduction itself

| Area | Status | Where | What counts as knowing it |
|---|---|---|---|
| What the reproduction establishes | Not yet | 54, `repro.qmd` | Which published tables are matched and to what precision |
| The one number that does not reproduce | Not yet | 73, `repro.qmd` | The U-bar rounding fork and why it is a fork rather than an error |
| The code layout | Not yet | `aiscen/` | Which file holds the steady state, the monthly loop, the scenarios |

---

## Question formats a test may use

1. **State it.** Define a symbol or name the seven inputs, from memory.
2. **Trace it.** Given a step, say what must already be known and what it produces.
3. **Move a dial.** Raise one input, predict the sign of the move in GDP, the two wages,
   and unemployment, and say through which equation.
4. **Spot the error.** A claim that is wrong in one specific way; find it.
5. **Read the number.** Given a figure or table from the deck, say what it does and does
   not license you to conclude.

## Log

- **2026-09-17.** Tracker created. Self-claimed at the start: main claims, the mapping
  exercise, and the seven inputs marked Solid; Part 2 marked Nearly throughout ("almost
  done understanding how the model is solved"). Nothing tested yet. Two questions asked
  while building the deck this week point at specific gaps to probe first: what f_C and
  f_N are, and why the Proposition 1 collapse check was a valid check on system (39).
