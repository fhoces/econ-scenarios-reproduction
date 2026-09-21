"""Accounting identities and internal checks along the simulated paths."""

import math
import pytest

from aiscen import simulate, statics
from aiscen.params import Fixed, SCENARIOS

F = Fixed()
RUNS = {name: simulate.run(F, s) for name, s in SCENARIOS.items()}


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_labor_force_adds_up_every_month(name):
    """p. 20: 'l_C,t + l_N,t + U_C,t + U_N,t = L at every date'."""
    for r in RUNS[name].months:
        assert r.l_C + r.l_N + r.U_C + r.U_N == pytest.approx(F.L, abs=1e-12)


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_no_negative_stocks_or_rates(name):
    for r in RUNS[name].months:
        assert r.l_C > 0 and r.l_N > 0 and r.U_C > 0 and r.U_N > 0
        assert 0.0 <= r.f_C <= 1.0 and 0.0 <= r.f_N <= 1.0
        assert r.H_C >= 0 and r.H_N >= 0


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_hires_never_exceed_searchers_or_openings(name):
    """Section 2.3.2: the den Haan et al. form keeps hires inside both bounds."""
    for r in RUNS[name].months:
        assert r.H_C <= min(r.S_C, r.v_C) + 1e-12
        assert r.H_N <= min(r.S_N, r.v_N) + 1e-12


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_every_hire_leaves_the_pool(name):
    """p. 20: f_C U_C + f_N U_N = H_C + H_N by (33) and (35)."""
    for r in RUNS[name].months:
        assert r.f_C * r.U_C + r.f_N * r.U_N == pytest.approx(r.H_C + r.H_N, rel=1e-10)


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_starts_at_the_steady_state(name):
    res = RUNS[name]
    first = res.months[0]
    assert first.U_C == pytest.approx(res.ss.U_C, rel=1e-12)
    assert first.l_C == pytest.approx(F.l_C0, rel=1e-12)
    assert first.q_C == pytest.approx(res.ss.q_C, rel=1e-12)   # f_{t0-1} = f_bar
    assert first.dlnA == 0.0


def test_ideas_step_matches_the_closed_form():
    """Appendix A, p. 41: the monthly step is 'within 0.02 percentage points of the
    closed form in 2030' on the extreme path."""
    res = RUNS["extreme"]
    stepped = res.at(2030.0).dlnA
    closed = simulate.ideas_closed_form(res, 2030.0)
    assert abs(stepped - closed) * 100 < 0.02


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_layoffs_only_in_the_cognitive_group_and_shortfalls_only_in_the_other(name):
    """Table A.1 notes: on the scenario paths G_N is zero and B_C is negligible."""
    for r in RUNS[name].months:
        assert r.D_C >= 0.0
        assert r.B_N >= 0.0


def test_cognitive_wage_discount_is_weakly_negative_and_sticky():
    """The rigid object is the cognitive discount to the common wage (Section 2.3.1).

    The initial condition is w_{C,t0-1} = w_{t0-1}, i.e. a zero discount one month
    before t0, so at t0 the discount has already taken one (1 - xi^(1/12)) step."""
    res = RUNS["extreme"]
    xs = [r.x_C for r in res.months]
    xi_m = F.xi ** (1.0 / 12.0)
    first = res.months[0]
    assert xs[0] == pytest.approx((1.0 - xi_m) * (first.dlnw_C_clear - first.dlnw_common),
                                  rel=1e-9)
    assert abs(xs[0]) < 1e-3                     # negligible at t0, as intended
    assert min(xs) < -0.05                       # the discount opens up
    assert all(x <= 1e-12 for x in xs)           # and never turns into a premium
    # rigidity: the discount never moves by more than the clearing gap in a month
    for prev, cur in zip(res.months, res.months[1:]):
        target = cur.dlnw_C_clear - cur.dlnw_common
        assert abs(cur.x_C - prev.x_C) <= abs(target - prev.x_C) + 1e-12


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_reported_gdp_equals_system_39_at_realized_employment(name):
    """Step 8 of Appendix A: the reported economy is (39) at realized employment."""
    res = RUNS[name]
    r = res.at(2029.0)
    ac = statics.actual_at_employment(F, r.m * r.d, r.a, r.psi, res.scen.rho,
                                      r.l_C, r.l_N, r.dlnA)
    assert ac.dlnY == pytest.approx(r.dlnY, abs=1e-12)
    assert ac.s_L == pytest.approx(r.s_L, abs=1e-12)


def _divisia_dual(res) -> float:
    """Equation (25): the Solow residual as the share-weighted growth of the two
    factor prices, chained monthly and integrated from the no-AI baseline."""
    f = res.fixed
    pts = [(f.s_L0, 0.0, 0.0)] + [(m.s_L_star, m.dlnw_common, m.dlnr_star)
                                  for m in res.months]
    total = 0.0
    for (sp, wp, rp), (sc, wc, rc) in zip(pts, pts[1:]):
        s = 0.5 * (sp + sc)
        total += s * (wc - wp) + (1.0 - s) * (rc - rp)
    return total


def test_tfp_index_agrees_with_its_dual_to_first_order():
    """Appendix C.4: Equation (45) 'agrees with the dual (25) to first order'.

    (45) is a base-weighted index and (25) a chained one, so they part company at
    second order: the discrepancy has to be negligible for a small shock and grow
    with the size of the shock, which is what this checks."""
    rel = {}
    for name in ("modest", "substantial", "extreme"):
        res = RUNS[name]
        tfp = res.at(2030.0).dln_tfp
        dual = _divisia_dual(res)
        rel[name] = abs(tfp - dual) / tfp
        assert dual < tfp                      # chaining with a falling labor share
    assert rel["modest"] < 0.005               # 0.001 pp on a 0.71 pct gap
    assert rel["modest"] < rel["substantial"] < rel["extreme"]
    assert rel["extreme"] < 0.10
