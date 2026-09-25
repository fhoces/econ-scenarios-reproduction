"""Tables 5 and 6 (pp. 37-38): the capital-supply and wage-rigidity variants."""

import pathlib
from dataclasses import replace

import pytest

from aiscen import simulate
from aiscen.params import Fixed, SCENARIOS
from aiscen.report import TABLE5, TABLE5_ROWS, TABLE6, TABLE6_ROWS, table3_column

F = Fixed()

# Every row is checked at the package default U_bar = 0.038 (Table 1), the same
# reading Table 3 and tests/test_printed_precision.py use. The all-workers rows sit
# 0.01 to 0.08 points low for the pool-rounding reason documented in
# tests/test_table3.py::test_pool_rounding_explains_the_two_wide_cells, well inside
# the tolerance below.


def tol(want: float) -> float:
    """0.12 points, or 0.4 percent of the published value if that is larger."""
    return max(0.12, 0.004 * abs(want))


@pytest.mark.parametrize("key,want", list(TABLE5.items()))
def test_table5(key, want):
    """Every Table 5 cell, at its capital-supply elasticity."""
    scen, eps = key
    col = table3_column(simulate.run(Fixed(eps=eps), SCENARIOS[scen]))
    for row, w in zip(TABLE5_ROWS, want):
        assert col[row] == pytest.approx(w, abs=tol(w)), f"{key} {row}"


@pytest.mark.parametrize("key,want", list(TABLE6.items()))
def test_table6(key, want):
    """Every Table 6 cell, at its wage rigidity."""
    scen, xi = key
    col = table3_column(simulate.run(Fixed(xi=xi), SCENARIOS[scen]))
    for row, w in zip(TABLE6_ROWS, want):
        assert col[row] == pytest.approx(w, abs=tol(w)), f"{key} {row}"


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

    # Footnote 14 (p. 37), also at eps = 1: the substantial scenario's m, d and a with
    # the extreme scenario's psi, mu and rho. README.md types its three figures: the GDP
    # gap, the fall in labor income as a share of no-AI GDP, and the transfer that would
    # hold the AI-sensitive occupations' income at its no-AI level, as a share of the
    # GDP gain (their no-AI wage bill is s_C,t0 of GDP). The last is repeated with
    # posting speed also at the extreme value, which the footnote does not say.
    readme = " ".join((pathlib.Path(__file__).resolve().parent.parent / "README.md")
                      .read_text().split())
    S, E = SCENARIOS["substantial"], SCENARIOS["extreme"]
    for theta_H, words in ((S.theta_H, "{t:.0f} percent here"),
                           (E.theta_H, "({t:.0f} percent if posting speed")):
        mix = replace(S, psi=E.psi, mu=E.mu, rho=E.rho, theta_H=theta_H)
        c = table3_column(simulate.run(Fixed(eps=1.0), mix))
        gdp = c["GDP, pct above no-AI"]
        transfer = -F.s_C0 * c["  wage bill of cognitive occs"] / gdp * 100
        assert words.format(t=transfer) in readme
        if theta_H == S.theta_H:
            assert f"({gdp:.2f} here)" in readme
            assert f"({-F.s_L0 * c['Labor income, pct above no-AI']:.2f} here)" in readme


# ---------------------------------------------------------------- slop extension ----

def test_displacement_does_not_depend_on_the_gain():
    """The mechanism behind the slop result: Equation (11)'s displacement term has no
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
    """critical_gain() returns the gain at which the average wage crosses zero."""
    from aiscen import slop
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
