"""Does every cell of Tables 3, 5 and 6 round to the digit the paper prints?

The rest of the suite checks the cells against a numerical tolerance, which is the
right test of the model. This module checks the strictly harder question behind the
prose in the README, the landing page, the report and the deck: which cells, rounded
half-up to the paper's own number of decimals, land on the published value (153 of
169) and which do not.

It is written as an exact allowlist rather than a tolerance, so that a cell moving in
or out of agreement fails here and the prose has to be updated with it.
"""

import pathlib
import re
from decimal import Decimal, ROUND_HALF_UP

import pytest

from aiscen import report, simulate
from aiscen.params import Fixed, SCENARIOS
from aiscen.report import table3_column
from aiscen.report import TABLE5, TABLE5_ROWS, TABLE6, TABLE6_ROWS

# Table 3 prints one decimal everywhere except the two ideas rows, which carry two.
DECIMALS = {
    "Ideas stock A, pct above no-AI": 2,
    "Growth of the ideas stock, pct per year": 2,
}

# (table, column, row) for every cell whose reproduced value rounds to a different
# printed digit than the paper's, at the package defaults (U_bar = 0.038, Table 1).
# Seven of these land at U_bar = 0.0384, the pool rounding fork; see
# test_the_pool_fork_fixes_seven_of_them... below. None is off by more than 0.11.
KNOWN_DIFFERENT = {
    ("Table 3", "modest", "GDP, index 2024 = 100"),
    ("Table 3", "extreme", "GDP growth, pct per year"),
    ("Table 3", "extreme", "Cognitive employment, pct since mid-2026"),
    ("Table 3", "No AI", "Unemployment rate, cognitive, pct"),
    ("Table 3", "substantial", "Unemployment rate, all workers, pct"),
    ("Table 3", "substantial", "Growth of the ideas stock, pct per year"),
    ("Table 3", "extreme", "Growth of the ideas stock, pct per year"),
    ("Table 5", "substantial, eps=6.0", "GDP, pct above no-AI"),
    ("Table 6", "substantial, xi=0.5", "Unemployment rate, all workers, pct"),
    ("Table 6", "substantial, xi=0.75", "Unemployment rate, cognitive, pct"),
    ("Table 6", "substantial, xi=0.9", "Unemployment rate, all workers, pct"),
    ("Table 6", "extreme, xi=0.0", "  cognitive occupations w_C"),
    ("Table 6", "extreme, xi=0.5", "Cognitive employment, pct since mid-2026"),
    ("Table 6", "extreme, xi=0.75", "Cognitive employment, pct since mid-2026"),
    ("Table 6", "extreme, xi=0.75", "Unemployment rate, cognitive, pct"),
    ("Table 6", "extreme, xi=0.9", "Unemployment rate, all workers, pct"),
}

TOTAL_CELLS = 169          # 80 + 40 + 49
LARGEST_GAP = 0.11         # percentage points, the extreme xi=0 cognitive wage


def round_half_up(x: float, decimals: int) -> float:
    """Round the way a table's typesetter does: .5 goes away from zero."""
    return float(Decimal(repr(x)).quantize(Decimal(1).scaleb(-decimals),
                                           rounding=ROUND_HALF_UP))


def _all_cells(U_bar: float = None):
    """Yield (table, column, row, reproduced, published) for all 169 compared cells."""
    kw = {} if U_bar is None else {"U_bar": U_bar}
    t3 = report.build_table3(Fixed(**kw))
    for row in report.ROW_ORDER:
        for col, got, want in zip(("No AI", "modest", "substantial", "extreme"),
                                  t3[row], report.PUBLISHED[row]):
            yield "Table 3", col, row, got, want
    for (scen, eps), want_col in TABLE5.items():
        col = table3_column(simulate.run(Fixed(eps=eps, **kw), SCENARIOS[scen]))
        for row, want in zip(TABLE5_ROWS, want_col):
            yield "Table 5", f"{scen}, eps={eps}", row, col[row], want
    for (scen, xi), want_col in TABLE6.items():
        col = table3_column(simulate.run(Fixed(xi=xi, **kw), SCENARIOS[scen]))
        for row, want in zip(TABLE6_ROWS, want_col):
            yield "Table 6", f"{scen}, xi={xi}", row, col[row], want


def _misses(U_bar: float = None) -> dict:
    """The cells that round to a different printed digit, keyed (table, column, row)."""
    out = {}
    for table, col, row, got, want in _all_cells(U_bar):
        if round_half_up(got, DECIMALS.get(row, 1)) != want:
            out[(table, col, row)] = (got, want)
    return out


MISSES = _misses()


def test_the_compared_grid_is_169_cells():
    """80 Table 3 cells + 40 Table 5 + 49 Table 6, the count the prose quotes."""
    assert sum(1 for _ in _all_cells()) == TOTAL_CELLS


def test_exactly_the_allowlisted_cells_miss_the_printed_digit():
    """The prose in README.md, index.html, repro.qmd and slides.Rmd quotes these counts."""
    assert set(MISSES) == KNOWN_DIFFERENT, (
        f"newly different: {sorted(set(MISSES) - KNOWN_DIFFERENT)}; "
        f"now agreeing: {sorted(KNOWN_DIFFERENT - set(MISSES))}")
    assert len(KNOWN_DIFFERENT) == 16
    assert sum(1 for k in KNOWN_DIFFERENT if k[0] == "Table 3") == 7
    assert sum(1 for k in KNOWN_DIFFERENT if k[0] == "Table 5") == 1
    assert sum(1 for k in KNOWN_DIFFERENT if k[0] == "Table 6") == 8
    # README.md lists the sixteen cells as "| table | cell | reproduced | published |":
    # the reproduced value one decimal finer than the paper prints, the published one as
    # printed. Every miss must appear there, and the table must have no extra row.
    readme = (pathlib.Path(__file__).resolve().parent.parent / "README.md").read_text()
    listed = [ln for ln in readme.splitlines() if re.match(r"\| Table [356] \| .* \| -?[\d.]+ \| -?[\d.]+ \|$", ln)]
    assert len(listed) == len(MISSES)
    for (table, col, row), (got, want) in MISSES.items():
        d = DECIMALS.get(row, 1)
        assert any(ln.startswith(f"| {table} |") and ln.endswith(f"| {got:.{d + 1}f} | {want:.{d}f} |")
                   for ln in listed), f"README misses row for {table}, {col}, {row}"


def test_no_difference_is_larger_than_a_last_digit():
    """Every one of them is last-digit noise, not a modelling gap."""
    for key, (got, want) in MISSES.items():
        assert abs(got - want) <= LARGEST_GAP, f"{key}: {got} vs {want}"


def test_the_pool_fork_fixes_seven_of_them_but_not_the_no_ai_cognitive_rate():
    """At U_bar = 0.0384 (the p. 26 derivation's value) seven of the sixteen land.

    The all-workers rows all do, which is the headline of the U_bar story. The No-AI
    cognitive rate does not: it moves from 2.82 to 2.85, which still prints as 2.8
    against the paper's 2.9. So the fork explains that cell's size, not its printed digit.
    """
    fixed = _misses(0.0384)
    assert len(fixed) == 9
    healed = set(MISSES) - set(fixed)
    assert len(healed) == 7
    # Six of the seven are unemployment rows, which is the pool's own margin; the
    # seventh (Table 5's substantial eps=6 GDP cell) tips over coincidentally.
    assert sum(1 for _, _, row in healed if row.startswith("Unemployment rate")) == 6
    key = ("Table 3", "No AI", "Unemployment rate, cognitive, pct")
    assert key in fixed
    assert fixed[key][0] == pytest.approx(2.848, abs=0.002)
    assert round_half_up(fixed[key][0], 1) == 2.8
    # The all-workers cell, by contrast, lands exactly.
    assert ("Table 3", "substantial", "Unemployment rate, all workers, pct") not in fixed
