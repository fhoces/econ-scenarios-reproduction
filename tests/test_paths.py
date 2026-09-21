"""The exogenous paths against the numbers the paper states for them."""

import math
import pytest

from aiscen.params import Fixed, SCENARIOS
from aiscen.paths import Paths, research_share

F = Fixed()


def test_logistic_slopes_match_paper():
    """p. 48: 'kappa_m = 0.33, kappa_d = 0.51' for the substantial scenario."""
    p = Paths.build(F, SCENARIOS["substantial"])
    assert p.kappa_m == pytest.approx(0.33, abs=0.005)
    assert p.kappa_d == pytest.approx(0.51, abs=0.005)


@pytest.mark.parametrize("name,m,d,a", [
    ("modest", 0.20, 0.20, 0.30),
    ("substantial", 0.30, 0.40, 0.45),
    ("extreme", 0.50, 0.60, 0.80),
])
def test_paths_hit_their_2030_values(name, m, d, a):
    """Table 1, panel B: the 2030 values, and 'g_a ... imply a_2030 = 0.30/0.45/0.80'."""
    p = Paths.build(F, SCENARIOS[name])
    assert p.m(2030.0) == pytest.approx(m, abs=1e-10)
    assert p.d(2030.0) == pytest.approx(d, abs=1e-10)
    assert p.a(2030.0) == pytest.approx(a, abs=0.005)


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_paths_coincide_at_the_mid_2026_anchor(name):
    """Section 3.3: 'the scenarios coincide at mid-2026'."""
    p = Paths.build(F, SCENARIOS[name])
    assert p.m(F.t_anchor) == pytest.approx(0.14, abs=1e-10)
    assert p.d(F.t_anchor) == pytest.approx(0.10, abs=1e-10)


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_gdp_gap_at_t0_is_at_most_a_quarter_percent(name):
    """Appendix A, p. 40: at t0 the AI objects imply a GDP gap of at most 0.25 pct."""
    p = Paths.build(F, SCENARIOS[name])
    x = p.at(F.t0)
    assert F.s_L0 * x["md"] * x["a"] < 0.0025


def test_task_instances_performed_with_ai_in_2030():
    """Section 4.2: 'AI performs m d = 12 percent of the economy's task instances'."""
    p = Paths.build(F, SCENARIOS["substantial"])
    assert p.at(2030.0)["md"] == pytest.approx(0.12, abs=1e-10)


def test_research_share_path():
    """Appendix C.2: the research share goes from 3.5 pct in 2024 to 4.1 pct in 2030."""
    assert research_share(F, 2024.0) == pytest.approx(0.035, abs=1e-12)
    assert research_share(F, 2030.0) == pytest.approx(0.041, abs=0.0005)
    g_R = F.fishing_out_R * F.g / F.lam
    assert g_R == pytest.approx(0.048, abs=0.0005)          # 'research input to grow at 4.8 pct'
    assert g_R - (F.g + F.n) == pytest.approx(F.g_iota, abs=0.0005)
