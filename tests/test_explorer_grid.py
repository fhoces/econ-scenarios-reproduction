"""The precomputed grid the static explorer serves (explorer/grid.js).

Three things can silently rot there and none of them shows up as a broken page:
the eleven outcomes are indexed positionally by the JS, so any change to the tuple
in `slides/make_grid_app.py` has to keep `snap`, `outcomes` and `units` the same
length and order; the committed `grid.js` can fall behind the model; and the three
named scenarios, which the explorer advertises as sitting "at the corners of this
grid", can drift away from a real scenario run.

The last one is the interesting case. Every cell of the grid builds `a_t` from the
*substantial* mid-2026 anchor, because the explorer has no per-cell anchor to use,
so an off-anchor corner reproduces the scenario's 2030 levels but not a rate defined
over the preceding twelve months. GDP growth is the only such rate here, and it is
the only outcome allowed a wide tolerance below.
"""

import json
import math
import pathlib
import sys

import pytest

from aiscen.params import Fixed, Scenario, SCENARIOS, SUBSTANTIAL
import aiscen.simulate as sim

ROOT = pathlib.Path(__file__).resolve().parents[1]
GRID_JS = ROOT / "explorer" / "grid.js"
sys.path.insert(0, str(ROOT / "slides"))
import make_grid_app as mga  # noqa: E402

N_OUTCOMES = 11
GDP_GROWTH = 7          # the one path-dependent outcome; see the module docstring
LEVEL_TOL = 0.03        # what explorer/index.html promises for the other ten
GROWTH_TOL = 0.25       # what the extreme corner actually needs


@pytest.fixture(scope="module")
def grid():
    if not GRID_JS.exists():                       # pragma: no cover
        pytest.skip("explorer/grid.js not built; run python3 slides/make_grid_app.py")
    text = GRID_JS.read_text().strip()
    assert text.startswith("window.__GRID__=") and text.endswith(";")
    return json.loads(text[len("window.__GRID__="):-1])


def test_the_outcome_arrays_stay_the_same_length_and_order(grid):
    assert len(grid["outcomes"]) == len(grid["units"]) == N_OUTCOMES
    assert all(len(row) == N_OUTCOMES for row in grid["snap"])
    assert grid["outcomes"][GDP_GROWTH] == "GDP growth"
    # The displayed labels use the deck's terminology, not the paper's.
    assert not any("ognitive" in name for name in grid["outcomes"])


def test_the_dials_match_the_exporter(grid):
    assert [d["key"] for d in grid["dials"]] == [k for k, _, _, _ in mga.DIALS]
    assert [d["levels"] for d in grid["dials"]] == [list(lv) for _, _, _, lv in mga.DIALS]
    n = math.prod(len(lv) for _, _, _, lv in mga.DIALS)
    assert len(grid["snap"]) == n == 4374
    for key in ("gdp", "wage", "u"):
        assert len(grid[key]) == n
        assert all(len(p) == len(grid["t"]) for p in grid[key][:50])


def _cell_index(grid, levels):
    """Mixed-radix index, the same arithmetic the explorer's JS does."""
    idx = 0
    for level, dial in zip(levels, grid["dials"]):
        idx = idx * len(dial["levels"]) + level
    return idx


@pytest.mark.parametrize("name", ["modest", "substantial", "extreme"])
def test_the_named_corners_reproduce_their_scenario(grid, name):
    """Levels agree to 0.03; GDP growth does not, and the explorer says so."""
    cell = grid["snap"][_cell_index(grid, grid["named"][name])]
    res = sim.run(Fixed(), SCENARIOS[name])
    e, f = res.at(2030.0), Fixed()
    scenario = [
        100 * (math.exp(e.dlnY) - 1), 100 * (math.exp(e.dlnw_C_paid) - 1),
        100 * (math.exp(e.dlnK) - 1), 100 * (math.exp(e.dln_tfp) - 1),
        100 * e.s_L, 100 * e.u_rate_C, 100 * e.u_rate,
        100 * (f.g + f.n + res.growth("dlnY", 2030.0)),
        100 * (math.exp(e.dlnw_avg) - 1), 100 * e.u_rate_N,
        100 * (math.exp(e.dlnw_N) - 1),
    ]
    for i, (got, want) in enumerate(zip(cell, scenario)):
        tol = GROWTH_TOL if i == GDP_GROWTH else LEVEL_TOL
        assert got == pytest.approx(want, abs=tol), \
            f"{name}, {grid['outcomes'][i]}: grid {got} vs scenario {want:.3f}"


def test_the_common_anchor_is_what_moves_gdp_growth(grid):
    """Not noise: rebuild the extreme corner with its own anchor and it lands."""
    cell = grid["snap"][_cell_index(grid, grid["named"]["extreme"])]
    f, s = Fixed(), SCENARIOS["extreme"]
    own = 100 * (f.g + f.n + sim.run(f, s).growth("dlnY", 2030.0))
    assert abs(cell[GDP_GROWTH] - own) > LEVEL_TOL          # the corner is off
    years = 2030.0 - f.t_anchor
    a_2030 = s.a_anchor + s.g_a * years
    shared = sim.run(f, Scenario(
        name="grid", m_2030=s.m_2030, d_2030=s.d_2030, a_anchor=SUBSTANTIAL.a_anchor,
        g_a=(a_2030 - SUBSTANTIAL.a_anchor) / years,
        psi=s.psi, rho=s.rho, mu=s.mu, theta_H=s.theta_H))
    # Same 2030 gain, substantial's anchor: that alone reproduces the grid's number.
    assert 100 * (f.g + f.n + shared.growth("dlnY", 2030.0)) == \
        pytest.approx(cell[GDP_GROWTH], abs=0.05)


def test_the_json_twin_agrees_when_it_exists(grid):
    """make_grid_app.py writes grid_app.json and grid.js from one payload."""
    twin = ROOT / "slides" / "data" / "grid_app.json"
    if not twin.exists():                          # gitignored; only built locally
        pytest.skip("slides/data/grid_app.json not built")
    assert json.loads(twin.read_text()) == grid
