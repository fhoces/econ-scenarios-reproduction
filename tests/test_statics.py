"""Proposition 1 and the actual-economy system (39): internal consistency and the
worked example of Section 2.1.3."""

import math
import pytest

from aiscen import statics
from aiscen.params import Fixed, SCENARIOS
from aiscen.paths import Paths

F = Fixed()


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
@pytest.mark.parametrize("dlnA", [0.0, 0.006])
def test_system_39_at_the_targets_is_proposition_1(name, dlnA):
    """Table A.1, panel D: 'at the targets it [system 39] is Proposition 1'."""
    p = Paths.build(F, SCENARIOS[name])
    x = p.at(2030.0)
    fr = statics.frictionless(F, x["md"], x["a"], x["psi"], x["rho"], dlnA)
    ac = statics.actual_at_employment(F, x["md"], x["a"], x["psi"], x["rho"],
                                      fr.l_C_star, fr.l_N_star, dlnA)
    assert ac.dlnr == pytest.approx(fr.dlnr, abs=1e-10)
    assert ac.dlnY == pytest.approx(fr.dlnYL, abs=1e-10)
    assert ac.s_L == pytest.approx(fr.s_L, abs=1e-10)
    # one common wage at the targets, and it is Proposition 1's wage
    assert ac.dlnw_C_tilde == pytest.approx(fr.dlnw_tilde, abs=1e-10)
    assert ac.dlnw_N_tilde == pytest.approx(fr.dlnw_tilde, abs=1e-10)


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_shares_add_up(name):
    """The price index is the numeraire, so the expenditure shares sum to one."""
    p = Paths.build(F, SCENARIOS[name])
    x = p.at(2030.0)
    fr = statics.frictionless(F, x["md"], x["a"], x["psi"], x["rho"])
    ac = statics.actual_at_employment(F, x["md"], x["a"], x["psi"], x["rho"],
                                      fr.l_C_star * 0.98, fr.l_N_star)   # off the targets
    assert ac.s_C + ac.s_N + ac.s_K == pytest.approx(1.0, abs=1e-10)
    assert ac.s_L == pytest.approx(ac.s_C + ac.s_N, abs=1e-12)


def test_wage_identity():
    """Equation (5): Delta ln w = Delta ln(Y/L) + Delta ln s_L holds at every date."""
    p = Paths.build(F, SCENARIOS["extreme"])
    x = p.at(2029.0)
    fr = statics.frictionless(F, x["md"], x["a"], x["psi"], x["rho"], dlnA=0.004)
    assert fr.dlnw == pytest.approx(fr.dlnYL + fr.dln_sL, abs=1e-12)


def test_perfectly_elastic_capital_gives_caselli_manning():
    """Section 2.1.3: at eps = infinity the rental rate is pegged and the wage rises
    by the full TFP gain, Delta ln w = m d a (to first order)."""
    f = Fixed(eps=math.inf)
    fr = statics.frictionless(f, 0.12, 0.45, 0.75, 0.25)
    assert fr.dlnr == 0.0
    assert fr.dlnw == pytest.approx(0.12 * 0.45, abs=0.004)


def test_worked_example_of_section_213():
    """p. 12: 'Delta ln TFP_2030 approx 0.6 x 0.30 x 0.40 x 0.45 = 0.032 ...
    (The exact solution is 0.029.)'"""
    md, a = 0.30 * 0.40, 0.45
    first_order = F.s_L0 * md * a
    assert first_order == pytest.approx(0.032, abs=0.0005)
    fr = statics.frictionless(F, md, a, 0.75, 0.25)
    assert fr.dln_tfp == pytest.approx(0.029, abs=0.0005)


def test_labor_share_without_ai_is_the_base_share():
    fr = statics.frictionless(F, 0.0, 0.0, 0.75, 0.25)
    assert fr.s_L == pytest.approx(F.s_L0, abs=1e-12)
    assert fr.dlnr == pytest.approx(0.0, abs=1e-10)
    assert fr.dlnYL == pytest.approx(0.0, abs=1e-12)


@pytest.mark.parametrize("name,rtol", [("modest", 0.15), ("substantial", 0.30)])
def test_first_order_rows_track_the_exact_ones(name, rtol):
    """The '≈' rows of Table A.1 should agree with the exact rows for a small shock;
    the paper only claims first-order accuracy, so the tolerance is loose and scales
    with the size of the scenario."""
    p = Paths.build(F, SCENARIOS[name])
    x = p.at(2030.0)
    fo = statics.first_order(F, x["md"], x["a"], x["psi"], x["rho"])
    ex = statics.frictionless(F, x["md"], x["a"], x["psi"], x["rho"])
    assert fo.dlnr == pytest.approx(ex.dlnr, rel=rtol)
    assert fo.dln_sL == pytest.approx(ex.dln_sL, rel=rtol)
    assert fo.ell_N_tilde == pytest.approx(ex.ell_N_tilde, rel=rtol)
    assert fo.dln_tfp == pytest.approx(ex.dln_tfp, rel=rtol)
    assert fo.dlnYL == pytest.approx(ex.dlnYL, rel=rtol)


def test_first_order_rental_row_matches_the_worked_modest_case():
    """Hand computation from Table A.1's first-order rental row at the modest
    scenario's 2030 values: [0.012 + 0.35 x 0.05] / (3 + 5/6) = 0.0077."""
    fo = statics.first_order(F, 0.04, 0.30, 0.50, 0.50)
    assert fo.dlnr == pytest.approx(0.0077, abs=5e-5)
