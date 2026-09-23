"""Reporting: rebuild Table 3 of the paper (p. 31) from a simulation.

The paper reports level differences as percent deviations from the no-AI path,
exp(Delta ln x) - 1, and growth rates as log changes over the preceding twelve
months (note to Table 3). Both conventions are applied here.
"""

import math

from .params import Fixed, SCENARIOS
from . import simulate

PCT = 100.0


def pct(dln: float) -> float:
    """Percent above the no-AI path from a log gap."""
    return (math.exp(dln) - 1.0) * PCT


def table3_column(res: simulate.Result, t: float = 2030.0) -> dict:
    """One scenario column of Table 3."""
    f = res.fixed
    m = res.at(t)
    i = res.months.index(m)
    if i < 12:
        raise ValueError(f"Table 3 growth rows need 12 months of history before t = {t}")
    m12 = res.months[i - 12]
    l_C_2026 = res.at(f.t_anchor).l_C
    L_emp0 = f.l_C0 + f.l_N0

    w_C, w_N = math.exp(m.dlnw_C_paid), math.exp(m.dlnw_N)
    labor_income = w_C * m.l_C + w_N * m.l_N          # no-AI counterpart: 1 * L_emp0
    g_trend = f.g + f.n
    g_tfp_trend = f.s_L0 * f.g

    return {
        # A. Output
        "GDP, pct above no-AI": pct(m.dlnY),
        "GDP, index 2024 = 100": PCT * math.exp(g_trend * (t - f.t0) + m.dlnY),
        "GDP growth, pct per year": PCT * (g_trend + m.dlnY - m12.dlnY),
        # B. Factor prices and income shares
        "Average wage, pct above no-AI": pct(m.dlnw_avg),
        "  cognitive occupations w_C": pct(m.dlnw_C_paid),
        "  all other occupations w_N": pct(m.dlnw_N),
        "Net return r - delta, pct per year": PCT * (f.r_bar * math.exp(m.dlnr) - f.delta),
        "Capital stock, pct above no-AI": pct(m.dlnK),
        "Labor share, pct of income": PCT * m.s_L,
        "Capital share, pct of income": PCT * (1.0 - m.s_L),
        "Labor income, pct above no-AI": PCT * (labor_income / L_emp0 - 1.0),
        "  wage bill of cognitive occs": PCT * (w_C * m.l_C / f.l_C0 - 1.0),
        "Capital income, pct above no-AI": pct(m.dlnr + m.dlnK),
        # C. The labor market
        "Cognitive employment, pct since mid-2026": PCT * (m.l_C / l_C_2026 - 1.0),
        "Unemployment rate, cognitive, pct": PCT * m.u_rate_C,
        "Unemployment rate, all workers, pct": PCT * m.u_rate,
        # D. Technology
        "Measured TFP, pct above no-AI": pct(m.dln_tfp),
        "Measured TFP growth, pct per year": PCT * (g_tfp_trend + m.dln_tfp - m12.dln_tfp),
        "Ideas stock A, pct above no-AI": pct(m.dlnA),
        "Growth of the ideas stock, pct per year": PCT * (f.g + m.dlnA - m12.dlnA),
    }


def no_ai_column(f: Fixed, t: float = 2030.0) -> dict:
    """The 'No AI' column of Table 3."""
    from . import steady
    ss = steady.solve(f)
    return {
        "GDP, pct above no-AI": 0.0,
        "GDP, index 2024 = 100": PCT * math.exp((f.g + f.n) * (t - f.t0)),
        "GDP growth, pct per year": PCT * (f.g + f.n),
        "Average wage, pct above no-AI": 0.0,
        "  cognitive occupations w_C": 0.0,
        "  all other occupations w_N": 0.0,
        "Net return r - delta, pct per year": PCT * (f.r_bar - f.delta),
        "Capital stock, pct above no-AI": 0.0,
        "Labor share, pct of income": PCT * f.s_L0,
        "Capital share, pct of income": PCT * f.s_K0,
        "Labor income, pct above no-AI": 0.0,
        "  wage bill of cognitive occs": 0.0,
        "Capital income, pct above no-AI": 0.0,
        "Cognitive employment, pct since mid-2026": 0.0,
        "Unemployment rate, cognitive, pct": PCT * ss.U_C / (ss.U_C + f.l_C0),
        "Unemployment rate, all workers, pct": PCT * f.U_bar,
        "Measured TFP, pct above no-AI": 0.0,
        "Measured TFP growth, pct per year": PCT * f.s_L0 * f.g,
        "Ideas stock A, pct above no-AI": 0.0,
        "Growth of the ideas stock, pct per year": PCT * f.g,
    }


# Table 3 of the paper, transcribed for comparison (p. 31).
PUBLISHED = {
    "GDP, pct above no-AI": (0.0, 1.6, 8.3, 32.4),
    "GDP, index 2024 = 100": (112.7, 114.5, 122.1, 149.3),
    "GDP growth, pct per year": (2.0, 2.4, 5.4, 15.4),
    "Average wage, pct above no-AI": (0.0, 0.7, 2.1, 9.7),
    "  cognitive occupations w_C": (0.0, 0.4, -0.3, -11.5),
    "  all other occupations w_N": (0.0, 1.1, 5.9, 33.6),
    "Net return r - delta, pct per year": (6.5, 6.6, 7.0, 8.3),
    "Capital stock, pct above no-AI": (0.0, 2.3, 13.8, 56.3),
    "Labor share, pct of income": (60.0, 59.4, 56.1, 45.2),
    "Capital share, pct of income": (40.0, 40.6, 43.9, 54.8),
    "Labor income, pct above no-AI": (0.0, 0.6, 1.4, 0.5),
    "  wage bill of cognitive occs": (0.0, -0.3, -4.6, -31.0),
    "Capital income, pct above no-AI": (0.0, 3.1, 18.9, 81.4),
    "Cognitive employment, pct since mid-2026": (0.0, -0.5, -3.9, -21.5),
    "Unemployment rate, cognitive, pct": (2.9, 2.9, 4.5, 17.9),
    "Unemployment rate, all workers, pct": (3.8, 3.9, 4.6, 11.9),
    "Measured TFP, pct above no-AI": (0.0, 0.7, 3.1, 13.4),
    "Measured TFP growth, pct per year": (1.0, 1.2, 2.3, 7.3),
    "Ideas stock A, pct above no-AI": (0.0, 0.07, 0.20, 0.61),
    "Growth of the ideas stock, pct per year": (1.67, 1.69, 1.76, 2.02),
}

ROW_ORDER = list(PUBLISHED)


# Tables 5 and 6 of the paper (pp. 37-38), transcribed for comparison: the
# capital-supply (eps) and wage-rigidity (xi) variants, keyed by (scenario, value).
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


def build_table3(f: Fixed = None, t: float = 2030.0) -> dict:
    """Simulate all three scenarios and return {row: (no_ai, modest, subst, extreme)}."""
    f = f or Fixed()
    cols = {"No AI": no_ai_column(f, t)}
    for name in ("modest", "substantial", "extreme"):
        cols[name] = table3_column(simulate.run(f, SCENARIOS[name], t_end=t), t)
    return {row: tuple(cols[c][row] for c in ("No AI", "modest", "substantial", "extreme"))
            for row in ROW_ORDER}


def compare(f: Fixed = None, t: float = 2030.0) -> str:
    """Side-by-side of this reimplementation against the published Table 3."""
    mine = build_table3(f, t)
    head = f"{'Row':42s} {'No AI':>13s} {'Modest':>13s} {'Substantial':>13s} {'Extreme':>13s}"
    out = [head, "-" * len(head)]
    for row in ROW_ORDER:
        cells = []
        for got, want in zip(mine[row], PUBLISHED[row]):
            diff = abs(got - want)
            tol = 0.10 if abs(want) >= 10.0 else 0.05     # tests/test_table3.py::tol
            flag = " " if diff <= tol else "*"
            cells.append(f"{got:6.2f}/{want:5.2f}{flag}")
        out.append(f"{row:42s} " + " ".join(f"{c:>13s}" for c in cells))
    out.append("-" * len(head))
    out.append("cells shown as simulated/published; * = outside the test tolerance (0.05, or 0.10 at 10 and above)")
    return "\n".join(out)
