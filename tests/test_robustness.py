"""Tables 5 and 6 (pp. 37-38): the capital-supply and wage-rigidity variants."""

import math
import pytest

from aiscen import simulate
from aiscen.params import Fixed, SCENARIOS
from aiscen.report import table3_column

F = Fixed()

TABLE5_ROWS = [
    "GDP, pct above no-AI",
    "Average wage, pct above no-AI",
    "Net return r - delta, pct per year",
    "Capital stock, pct above no-AI",
    "Labor share, pct of income",
]

TABLE5 = {
    ("substantial", 1.0): (6.4, -1.6, 7.6, 9.3, 55.1),
    ("substantial", 3.0): (8.3, 2.1, 7.0, 13.8, 56.1),
    ("substantial", 6.0): (9.1, 3.7, 6.8, 15.7, 56.5),
    ("substantial", math.inf): (10.0, 5.6, 6.5, 18.2, 57.0),
    ("extreme", 1.0): (21.3, -9.2, 10.3, 33.5, 41.2),
    ("extreme", 3.0): (32.4, 9.7, 8.3, 56.3, 45.2),
    ("extreme", 6.0): (37.2, 18.3, 7.5, 67.1, 46.9),
    ("extreme", math.inf): (43.3, 30.1, 6.5, 82.2, 49.1),
}

TABLE6_ROWS = [
    "GDP, pct above no-AI",
    "Average wage, pct above no-AI",
    "  cognitive occupations w_C",
    "  all other occupations w_N",
    "Cognitive employment, pct since mid-2026",
    "Unemployment rate, cognitive, pct",
    "Unemployment rate, all workers, pct",
]

TABLE6 = {
    ("substantial", 0.5): (8.3, 2.1, -0.3, 5.9, -3.9, 4.5, 4.6),
    ("substantial", 0.75): (7.9, 2.2, 0.7, 4.5, -4.6, 5.1, 4.9),
    ("substantial", 0.9): (7.7, 2.3, 1.4, 3.7, -5.0, 5.4, 5.2),
    ("extreme", 0.0): (36.6, 1.6, -42.2, 70.1, -1.3, 2.6, 3.1),
    ("extreme", 0.5): (32.4, 9.7, -11.5, 33.6, -21.5, 17.9, 11.9),
    ("extreme", 0.75): (30.5, 11.1, -2.9, 25.8, -25.9, 21.7, 13.9),
    ("extreme", 0.9): (29.2, 11.9, 2.8, 21.1, -28.5, 24.0, 15.2),
}

# The all-workers unemployment row needs U_bar = 0.0384 (the value the p. 26
# derivation and the published pool split imply) rather than Table 1's rounded
# 0.038; see tests/test_table3.py::test_pool_rounding_explains_the_two_wide_cells.
POOL_SENSITIVE = "Unemployment rate, all workers, pct"


def tol(want: float) -> float:
    return max(0.12, 0.004 * abs(want))


@pytest.mark.parametrize("key,want", list(TABLE5.items()))
def test_table5(key, want):
    scen, eps = key
    col = table3_column(simulate.run(Fixed(eps=eps), SCENARIOS[scen]))
    for row, w in zip(TABLE5_ROWS, want):
        assert col[row] == pytest.approx(w, abs=tol(w)), f"{key} {row}"


@pytest.mark.parametrize("key,want", list(TABLE6.items()))
def test_table6(key, want):
    scen, xi = key
    f = Fixed(xi=xi)
    col = table3_column(simulate.run(f, SCENARIOS[scen]))
    col_pool = table3_column(simulate.run(Fixed(xi=xi, U_bar=0.0384), SCENARIOS[scen]))
    for row, w in zip(TABLE6_ROWS, want):
        got = col_pool[row] if row == POOL_SENSITIVE else col[row]
        assert got == pytest.approx(w, abs=tol(w)), f"{key} {row}"


def test_flexible_wage_puts_the_whole_cost_in_wages():
    """Section 4.6: at xi = 0 the cognitive wage takes the hit (-42 pct) and
    unemployment barely moves (2.6 pct against a normal 2.9)."""
    col = table3_column(simulate.run(Fixed(xi=0.0), SCENARIOS["extreme"]))
    assert col["  cognitive occupations w_C"] < -40.0
    assert col["Unemployment rate, cognitive, pct"] < 3.0


def test_inelastic_capital_flips_the_sign_of_the_wage():
    """Section 4.5: 'at eps = 1 the wage changes sign'."""
    col = table3_column(simulate.run(Fixed(eps=1.0), SCENARIOS["substantial"]))
    assert col["Average wage, pct above no-AI"] < 0.0


# ---------------------------------------------------------------- slop extension ----

def test_displacement_does_not_depend_on_the_gain():
    """The mechanism behind the slop result: Equation (19)'s displacement term has no
    a in it, while the weak-link cushion is proportional to a."""
    from aiscen import slop
    full = slop.decomposition(F, slop.BASE)
    half = slop.decomposition(F, slop.scale_gain(slop.BASE, full["a_2030"] / 2))
    assert half["displacement"] == pytest.approx(full["displacement"], rel=1e-12)
    assert half["weak-link cushion"] == pytest.approx(full["weak-link cushion"] / 2, rel=1e-9)
    assert half["ratio"] > full["ratio"]


def test_slop_raises_the_wage_threshold_through_the_calibrated_elasticity():
    """eps* contains (1 - rho)/a, so a lower gain pushes it up. At the baseline gain
    it sits below eps = 3; halving the gain pushes it above."""
    from aiscen import slop
    a0 = slop.gain_2030(slop.BASE)
    assert slop.eps_star(F, slop.BASE) < F.eps
    assert slop.eps_star(F, slop.scale_gain(slop.BASE, a0 / 2)) > F.eps


def test_critical_gain_is_where_the_wage_changes_sign():
    from aiscen import slop
    from aiscen.report import table3_column
    a_crit = slop.critical_gain(F)
    assert 0.15 < a_crit < 0.35
    below = table3_column(simulate.run(F, slop.scale_gain(slop.BASE, a_crit * 0.8)))
    above = table3_column(simulate.run(F, slop.scale_gain(slop.BASE, a_crit * 1.2)))
    assert below["Average wage, pct above no-AI"] < 0 < above["Average wage, pct above no-AI"]


def test_zero_gain_still_raises_gdp_and_lowers_the_wage():
    """With no cost saving at all, automation still substitutes an accumulable factor
    for a fixed one, so output rises while labor pays for it."""
    from aiscen import slop
    col = table3_column(simulate.run(F, slop.scale_gain(slop.BASE, 1e-6)))
    assert col["GDP, pct above no-AI"] > 3.0
    assert col["Measured TFP, pct above no-AI"] < 0.5
    assert col["Average wage, pct above no-AI"] < -1.0
    assert col["Capital stock, pct above no-AI"] > 10.0
