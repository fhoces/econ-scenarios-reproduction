"""Numbers typed into the explorer page and the slide deck, recomputed.

The report computes its inline numbers when it renders, and the deck reads most of its
numbers from CSVs, but a handful of figures are written into the prose by hand: the
explorer's popups and grid note, and a few deck boxes. Each test here recomputes one
such figure, formats it the way the prose prints it, and checks that string is still
in the file, so a change to the model or the grid that moves a number fails here
instead of leaving the prose stale.
"""

import json
import math
import pathlib
import re
from dataclasses import replace

from aiscen import simulate, slop
from aiscen.params import SCENARIOS, Fixed, gain_path, scenario_from_2030_values
from aiscen.report import table3_column

ROOT = pathlib.Path(__file__).resolve().parent.parent
F = Fixed()
S = SCENARIOS["substantial"]

UC = "Unemployment rate, cognitive, pct"


def _text(rel: str) -> str:
    """File text with JS string concatenations joined and whitespace collapsed."""
    raw = (ROOT / rel).read_text()
    raw = re.sub(r'"\s*\+\s*"', "", raw)
    return re.sub(r"\s+", " ", raw)


EXPLORER = _text("explorer/index.html")
DECK = _text("slides/slides.Rmd")


# Format the way the prose prints: one or two decimals, and the deck's U+2212 minus.
def f1(x):
    """One decimal, the way most of the prose prints a number."""
    return f"{x:.1f}"


def f2(x):
    """Two decimals."""
    return f"{x:.2f}"


def neg(x, fmt=f1):
    """Format with the deck's U+2212 minus sign for negatives."""
    return ("−" + fmt(-x)) if x < 0 else fmt(x)


# ---------------------------------------------------------------- explorer grid ----

def _grid():
    """The committed explorer/grid.js as a dict."""
    s = (ROOT / "explorer" / "grid.js").read_text()
    return json.loads(s[s.index("=") + 1:].rstrip().rstrip(";"))


G = _grid()
KEYS = [d["key"] for d in G["dials"]]
SIZES = [len(d["levels"]) for d in G["dials"]]
LEVELS = {d["key"]: d["levels"] for d in G["dials"]}
GDP, WAGE_C, CAP, TFP, LSHARE, U_C, U_ALL, GROWTH, WAGE = range(9)


def _idx(levels):
    """Mixed-radix cell index from a list of level indices, as the explorer's JS does."""
    i = 0
    for k, v in enumerate(levels):
        i = i * SIZES[k] + v
    return i


def _cell(base, **moves):
    """Snapshot of the named corner `base` with some dials moved to given values."""
    lv = list(G["named"][base])
    for key, value in moves.items():
        lv[KEYS.index(key)] = LEVELS[key].index(value)
    return G["snap"][_idx(lv)]


def _grid_substantial():
    """The substantial corner as the grid builds it (gain landing exactly on 0.45)."""
    a_anchor, g_a = gain_path(0.45, S.a_anchor, 2030.0 - F.t_anchor)
    return replace(S, a_anchor=a_anchor, g_a=g_a)


GS = _grid_substantial()


def _spread(key, values):
    """One dial moved alone from the substantial corner, recomputed exactly: the grid
    stores two decimals, so differencing its snapshots can be off by 0.01."""
    if key == "m":
        scens = [replace(GS, m_2030=v) for v in values]
    elif key == "d":
        scens = [replace(GS, d_2030=v) for v in values]
    elif key == "a":
        scens = [replace(GS, **dict(zip(("a_anchor", "g_a"),
                                        gain_path(v, S.a_anchor, 2030.0 - F.t_anchor))))
                 for v in values]
    else:
        scens = [replace(GS, **{key: v}) for v in values]
    vals = [table3_column(simulate.run(F, sc))[UC] for sc in scens]
    return max(vals) - min(vals)


def test_explorer_psi_popup():
    """The automation-share popup: labor share and TFP at psi = 0.5 and 0.9."""
    lo, hi = _cell("substantial", psi=0.5), _cell("substantial", psi=0.9)
    assert (f"labor share from {f1(lo[LSHARE])} to {f1(hi[LSHARE])} percent while measured "
            f"TFP moves only from {f2(lo[TFP])} to {f2(hi[TFP])}") in EXPLORER
    # The parenthesis quotes the deck's figures for the same sweep, run on the paper's own
    # gain path (2030 gain 0.448) rather than the grid's 0.45 label.
    tfp = "Measured TFP, pct above no-AI"
    dlo, dhi = _col(psi=0.5), _col(psi=0.9)
    a_2030 = S.a_anchor + S.g_a * (2030.0 - F.t_anchor)
    assert (f"({f2(dlo[tfp])} to {f2(dhi[tfp])} on the scenario's own path, whose 2030 gain is "
            f"{a_2030:.3f} rather than this grid's 0.45") in EXPLORER


def test_explorer_gain_popup_minutes():
    """The gain popup's worked instance: 100 minutes becomes exp(-a) x 100."""
    m = [round(100 * math.exp(-a)) for a in (0.30, 0.45, 0.80)]
    assert f"at 0.30 a task that took 100 minutes takes {m[0]}, at 0.45 it takes {m[1]}, " \
           f"at 0.80 it takes {m[2]}" in EXPLORER


def test_explorer_one_at_a_time_ranges():
    """The popups' one-dial-at-a-time spreads of cognitive unemployment, and their ranking."""
    rho6 = _spread("rho", LEVELS["rho"])
    rho3 = _spread("rho", [0.5, 0.25, 0.0])
    mu, th, psi = (_spread(k, LEVELS[k]) for k in ("mu", "theta_H", "psi"))
    others = [_spread(k, LEVELS[k]) for k in KEYS if k != "rho"]
    assert f"by {f2(rho6)} points over the six values offered here" in EXPLORER
    assert rho6 > max(others)                               # "a shade more than any other"
    assert f"over the paper's own three levels it moves it by {f2(rho3)}" in EXPLORER
    assert f"unemployment by {f2(mu)} points over the paper's three levels" in EXPLORER
    assert mu == max(mu, rho3, psi, th)                     # widest of the four (panel C)
    assert f"unemployment by {f2(th)} points" in EXPLORER
    assert th == min(mu, rho3, psi, th)                     # smallest of the four


def test_explorer_highest_gdp_cell_is_extreme_with_normal_search():
    """The "Highest GDP cell" preset is the extreme corner with mu at its normal 0.17."""
    best = max(range(len(G["snap"])), key=lambda i: G["snap"][i][GDP])
    assert G["snap"][best] == _cell("extreme", mu=0.17)


def test_explorer_note_numbers():
    """The note under the dials: 0.448, and the grid-versus-run gaps it discloses."""
    run = {n: table3_column(simulate.run(F, SCENARIOS[n])) for n in ("substantial", "extreme")}
    sub, ext = _cell("substantial"), _cell("extreme")
    assert f"{S.a_anchor + S.g_a * (2030.0 - F.t_anchor):.3f}" == "0.448"
    assert "only reaches a 2030 gain of 0.448" in EXPLORER
    assert (f"GDP gap reads {f2(sub[GDP])} against "
            f"{f2(run['substantial']['GDP, pct above no-AI'])}") in EXPLORER
    assert (f"average wage {f2(sub[WAGE])} against "
            f"{f2(run['substantial']['Average wage, pct above no-AI'])}") in EXPLORER
    assert (f"it reads {f2(ext[GROWTH])} here against that scenario's own "
            f"{f2(run['extreme']['GDP growth, pct per year'])}") in EXPLORER


def test_explorer_corners_against_their_runs():
    """'the extreme corner lands within 0.03 points', 'the modest corner matches its run'."""
    def gap(name):
        """Largest gap between the grid's corner cell and the scenario's own run, over seven outcomes."""
        r = simulate.run(F, SCENARIOS[name])
        c = table3_column(r)
        own = [c["GDP, pct above no-AI"], c["  cognitive occupations w_C"],
               c["Capital stock, pct above no-AI"], c["Measured TFP, pct above no-AI"],
               c["Labor share, pct of income"], c[UC], c["Unemployment rate, all workers, pct"]]
        return max(abs(a - b) for a, b in zip(_cell(name), own))
    assert gap("extreme") < 0.03 and gap("substantial") < 0.03
    assert gap("modest") < 0.006                            # the grid stores 2 decimals
    assert "within 0.03 points" in EXPLORER and "the modest corner matches its run" in EXPLORER


def test_explorer_reinstatement_075_count():
    """How many rho = 0.75 cells end with a labor share above 60 percent."""
    ri = KEYS.index("rho")
    above = total = 0
    for i, snap in enumerate(G["snap"]):
        n, lv = i, []
        for k in range(len(SIZES) - 1, -1, -1):
            lv.insert(0, n % SIZES[k])
            n //= SIZES[k]
        if LEVELS["rho"][lv[ri]] == 0.75:
            total += 1
            above += snap[LSHARE] > 60
    assert f"above 60 percent in {above} of that level's {total} cells" in EXPLORER


def test_explorer_table_caption():
    """The table caption's three grid-versus-paper cells, and that they still differ."""
    from aiscen.report import PUBLISHED
    sub, ext = _cell("substantial"), _cell("extreme")
    p_w = PUBLISHED["Average wage, pct above no-AI"][2]
    p_u = PUBLISHED["Unemployment rate, all workers, pct"][2]
    p_g = PUBLISHED["GDP growth, pct per year"][3]
    assert f"substantial average wage ({f1(sub[WAGE])} here, {p_w} in the paper)" in EXPLORER
    assert f"all-workers unemployment ({f1(sub[U_ALL])} against {p_u})" in EXPLORER
    assert f"extreme GDP growth ({f1(ext[GROWTH])} against {p_g})" in EXPLORER
    for got, want in ((sub[WAGE], p_w), (sub[U_ALL], p_u), (ext[GROWTH], p_g)):
        assert f1(got) != f"{want:.1f}"                     # still genuinely different


def test_explorer_printed_digit_count():
    """"153 of them to the printed digit" follows the allowlist in test_printed_precision,
    and the suite's own size, typed in seven places, follows the suite."""
    from tests.test_printed_precision import MISSES
    assert f"{169 - len(MISSES)} of them to the printed digit" in EXPLORER

    # The test count (129) is typed into the README twice, the Makefile, the landing page
    # twice (with its 102 / 7 / 16 / 4 breakdown) and the deck twice. Count the suite by
    # collecting it in a separate pytest process, so the check holds however this run was
    # filtered (-k, a single file): collecting runs no tests, it only lists them.
    import subprocess
    import sys
    out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "tests"],
                         cwd=ROOT, capture_output=True, text=True).stdout
    ids = [ln for ln in out.splitlines() if "::" in ln]
    n = len(ids)
    grid = sum(1 for i in ids if i.startswith("tests/test_explorer_grid.py::"))
    prose = sum(1 for i in ids if i.startswith("tests/test_prose_numbers.py::"))
    rob = (ROOT / "tests/test_robustness.py").read_text()
    slop_n = len(re.findall(r"^def test_", rob.split("slop extension", 1)[1], flags=re.M))
    typed = {
        "README.md": [r"runs the (\d+) tests", r"# (\d+) tests:"],
        "Makefile": [r"the (\d+)-test validation suite"],
        "index.html": [r"The model, the (\d+)-test validation suite", r"(\d+) automated tests:"],
        "slides/slides.Rmd": [r"the model, (\d+) tests and every CSV"],
    }
    found = 0
    for rel, pats in typed.items():
        text = _text(rel)
        for pat in pats:
            hits = re.findall(pat, text)
            assert hits and all(int(h) == n for h in hits), (rel, pat, hits, n)
            found += len(hits)
    assert found == 7
    assert (f"{n} automated tests: {n - grid - prose - slop_n} core tests" in _text("index.html")
            and f"; {grid} that pin the explorer's precomputed grid" in _text("index.html")
            and f"; {prose} that recompute the numbers" in _text("index.html")
            and f"and {slop_n} for the <code>slop.py</code> extension" in _text("index.html"))


# ------------------------------------------------------------------------ deck ----

def _col(**moves):
    """Table 3 column of the substantial scenario with some inputs replaced."""
    return table3_column(simulate.run(F, replace(S, **moves)))


def test_deck_psi_full_range():
    """The deck's psi box over the full 0 to 1 range."""
    lo, hi = _col(psi=0.0), _col(psi=1.0)
    tfp, ls = "Measured TFP, pct above no-AI", "Labor share, pct of income"
    emp, gdp = "Cognitive employment, pct since mid-2026", "GDP, pct above no-AI"
    assert f"**{f2(lo[tfp])} to {f2(hi[tfp])}**" in DECK
    assert f"labor share moves **{f1(lo[ls])} to {f1(hi[ls])}**" in DECK
    assert f"**{neg(lo[emp])}% to {neg(hi[emp])}%**" in DECK
    assert f"GDP does rise over that range ({f1(lo[gdp])} to {f1(hi[gdp])})" in DECK


def test_deck_psi_paper_range():
    """The deck's psi box over the paper's 0.5 to 0.9 range."""
    lo, hi = _col(psi=0.5), _col(psi=0.9)
    assert (f"labor share from {f1(lo['Labor share, pct of income'])} to "
            f"{f1(hi['Labor share, pct of income'])} percent while TFP moves only "
            f"{f2(lo['Measured TFP, pct above no-AI'])} to "
            f"{f2(hi['Measured TFP, pct above no-AI'])}") in DECK


def test_deck_one_at_a_time_ranges():
    """The deck's one-dial-at-a-time spreads, on the scenario's own gain path."""
    def spread(**pairs):
        """Change in 2030 cognitive unemployment when one input moves between two values."""
        (k, (a, b)), = pairs.items()
        return abs(_col(**{k: a})[UC] - _col(**{k: b})[UC])
    rho, mu = spread(rho=(0.5, 0.0)), spread(mu=(0.17, 0.04))
    psi, th = spread(psi=(0.5, 0.9)), spread(theta_H=(0.1, 0.5))
    a_lo = scenario_from_2030_values("lo", 0.3, 0.4, 0.30, 0.75, 0.08)
    a_hi = scenario_from_2030_values("hi", 0.3, 0.4, 0.80, 0.75, 0.08)
    gain = abs(table3_column(simulate.run(F, a_hi))[UC] - table3_column(simulate.run(F, a_lo))[UC])
    assert (f"shifts 2030 AI-sensitive unemployment by {f2(rho)} points across the paper's range, "
            f"behind search efficiency $\\mu$ at {f2(mu)} and ahead of $\\psi$ at {f2(psi)}") in DECK
    assert f"shifts 2030 AI-sensitive unemployment by {f2(th)} points" in DECK
    assert f"only the gain $a$ moves it less, by {f2(gain)}" in DECK
    assert gain < th < psi < rho < mu


def test_deck_pool_rounding_box():
    """The verification box's two U-bar gaps and the 0.0384 rerun."""
    from aiscen.report import PUBLISHED, build_table3
    t3, t3b = build_table3(), build_table3(Fixed(U_bar=0.0384))
    all_gap = PUBLISHED["Unemployment rate, all workers, pct"][2] - t3["Unemployment rate, all workers, pct"][2]
    cog_gap = PUBLISHED[UC][0] - t3[UC][0]
    assert f"all-workers rate is {f2(all_gap)} points low" in DECK
    assert f"AI-sensitive rate {f2(cog_gap)} low" in DECK
    assert f"{f2(t3b[UC][0])} and still prints as 2.8 against 2.9" in DECK


def test_deck_slop_numbers():
    """The slop slides' typed numbers: the pure-slop row, the checking-becomes-work case,
    the displacement-versus-cushion table with its eps* values, and the critical gain."""
    pure = table3_column(simulate.run(F, slop.scale_gain(slop.BASE, 1e-6)))
    assert (f"GDP **+{f1(pure['GDP, pct above no-AI'])} percent**, capital "
            f"**+{f1(pure['Capital stock, pct above no-AI'])}**, measured TFP "
            f"**+{f1(pure['Measured TFP, pct above no-AI'])}**, average wage "
            f"**{neg(pure['Average wage, pct above no-AI'])}**, AI-sensitive wage "
            f"**{neg(pure['  cognitive occupations w_C'])}**") in DECK
    rows = {r["case"]: r for r in slop.cases(F)}
    work = rows["gain halved, checking becomes new human work"]
    assert f"average wage still rises (+{f1(work['Average wage, pct above no-AI'])})" in DECK
    assert f"labor share to {f1(work['Labor share, pct of income'])}" in DECK
    # The slop-mechanism slide: Equation (11)'s displacement term against the weak-link
    # cushion at the substantial gain, half of it, and the survey's lower quartile 0.09,
    # then the eps* threshold each implies, and the critical gain of the postscript box.
    a0 = slop.gain_2030(slop.BASE)
    eps = []
    for a in (a0, a0 / 2, 0.09):
        scen = slop.scale_gain(slop.BASE, a)
        d = slop.decomposition(F, scen)
        assert (f"| {d['a_2030']:.2f} | {f2(100 * d['displacement'])} pp | "
                f"{f2(100 * d['weak-link cushion'])} pp | {d['ratio']:.1f}x |") in DECK
        eps.append(f2(slop.eps_star(F, scen)))
    assert f"elasticity from {eps[0]} to {eps[1]} and then {eps[2]} across the three rows" in DECK
    assert f"falls below **{f2(slop.critical_gain(F))}**" in DECK


def test_deck_squeeze():
    """Section 2.1.2's Equation (7) margin at 2030: dln r minus the AI-sensitive wage paid."""
    sq = []
    for n in ("modest", "substantial", "extreme"):
        e = simulate.run(F, SCENARIOS[n]).at(2030.0)
        sq.append(f"{e.dlnr - e.dlnw_C_paid:.3f}")
    assert f"the squeeze reaches **{' / '.join(sq)}** log points" in DECK


def test_deck_pool_rounding_backup():
    """The U-bar backup slide restates the verification box's numbers with more detail."""
    from aiscen.report import PUBLISHED, TABLE6, TABLE6_ROWS, build_table3
    t3, t3b = build_table3(), build_table3(Fixed(U_bar=0.0384))
    UA = "Unemployment rate, all workers, pct"
    gap = {r: [p - g for p, g in zip(PUBLISHED[r], t3[r])] for r in (UC, UA)}
    assert (f"all-workers unemployment rate is {f2(gap[UA][2])} points low in the substantial "
            f"scenario ({f2(t3[UA][2])} against {PUBLISHED[UA][2]})") in DECK
    assert (f"AI-sensitive rate {f2(gap[UC][0])} points low in the No-AI column "
            f"({f2(t3[UC][0])} against {PUBLISHED[UC][0]})") in DECK
    others = [abs(g) for r in (UC, UA) for i, g in enumerate(gap[r])
              if (r, i) not in ((UA, 2), (UC, 0))]
    assert max(others) <= 0.04 and "every other column is within 0.04" in DECK
    # Table 6 unemployment cells as far off as the two Table 3 ones, and that one of
    # them is the Table 3 substantial run itself (xi at its default).
    far = []
    for (scen, xi), want in TABLE6.items():
        col = table3_column(simulate.run(Fixed(xi=xi), SCENARIOS[scen]))
        for i in (TABLE6_ROWS.index(UC), TABLE6_ROWS.index(UA)):
            g = want[i] - col[TABLE6_ROWS[i]]
            if g >= 0.065:
                far.append((scen, xi, g))
    assert len(far) == 4
    assert f"cells {f2(min(g for *_, g in far))} to {f2(max(g for *_, g in far))} low" in DECK
    assert ("substantial", F.xi) in [(s, x) for s, x, _ in far]
    assert "four Table 6 unemployment cells" in DECK
    assert f"all-workers row lands on {f1(t3b[UA][2])}" in DECK and f1(t3b[UA][2]) == f"{PUBLISHED[UA][2]}"
    assert f"improves only to {f2(t3b[UC][0])}, still printing as 2.8 against" in DECK
