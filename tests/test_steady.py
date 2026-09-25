"""The normal-times steady state against Section 2.3.2 and Section 3.2."""

import pytest

from aiscen import steady
from aiscen.params import Fixed

F = Fixed()
SS = steady.solve(F)


def test_cross_group_switching_is_one_in_seven():
    """p. 21: mu_bar = 0.17 is 'the value at which the share of job-finders in this
    steady state who change groups equals one in seven'; p. 26 reports 14.3 pct."""
    assert SS.switch_share == pytest.approx(1.0 / 7.0, abs=0.002)


def test_aggregate_finding_rate():
    """p. 26: 'at that value the finding rate in the model's steady state is 0.23 a month'."""
    assert SS.f_agg == pytest.approx(0.23, abs=0.005)


def test_filling_rates_and_matching_efficiency():
    """p. 21: 'The filling rates are 0.66 and 0.64, and chi is 0.76'.

    pi_N is 0.635 at Table 1's U_bar = 0.038, which prints as 0.63; it reaches the
    paper's 0.64 only at the p. 26 pool of 0.0384, the same rounding fork as Table 3."""
    assert SS.pi_C == pytest.approx(0.66, abs=0.005)
    assert SS.pi_N == pytest.approx(0.635, abs=0.001)
    assert steady.solve(Fixed(U_bar=0.0384)).pi_N == pytest.approx(0.64, abs=0.005)
    assert SS.chi == pytest.approx(0.76, abs=0.005)


def test_pool_split_matches_paper():
    """p. 21: the pool splits into 1.76 pct of the labor force of cognitive origin and
    2.08 of other origin. The paper's split uses U_bar = 3.84 pct (p. 26), Table 1
    rounds it to 3.8; the proportions are what the steady state pins down."""
    f = Fixed(U_bar=0.0384)
    ss = steady.solve(f)
    assert ss.U_C * 100 == pytest.approx(1.76, abs=0.005)   # 1.741 at U_bar = 0.038 fails
    assert ss.U_N * 100 == pytest.approx(2.08, abs=0.005)   # 2.059 at U_bar = 0.038 fails
    assert ss.U_C / (ss.U_C + f.l_C0) * 100 == pytest.approx(2.9, abs=0.06)
    assert ss.U_N / (ss.U_N + f.l_N0) * 100 == pytest.approx(5.4, abs=0.06)


def test_quit_rates_by_group():
    """p. 26: 'gives 0.63 percent a month for cognitive workers and 1.40 for all other'."""
    assert F.q_bar_C * 100 == pytest.approx(0.63, abs=0.01)
    assert F.q_bar_N * 100 == pytest.approx(1.40, abs=0.01)


def test_redundant_flow_condition_holds():
    """Table A.1, panel E note: one of the ten conditions is redundant, so the
    all-other origin's flow balance must hold at the solution."""
    assert abs(steady.check_redundant_condition(F, SS)) < 1e-12


def test_hires_replace_quits():
    """Equation (38): H_bar = q_bar l_t0 = f_bar U_bar, group by group."""
    assert SS.H_C == pytest.approx(SS.q_C * F.l_C0, rel=1e-12)
    assert SS.H_N == pytest.approx(SS.q_N * F.l_N0, rel=1e-12)
    assert SS.f_C * SS.U_C == pytest.approx(SS.H_C, rel=1e-9)
    assert SS.f_N * SS.U_N == pytest.approx(SS.H_N, rel=1e-9)
