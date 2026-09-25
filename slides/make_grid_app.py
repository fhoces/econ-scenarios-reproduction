"""Export every cell of the dial grid (3^6 x 6 = 4374 cells), with paths, for the explorer.

Writes explorer/grid.js, the file the explorer page loads, and its gitignored JSON twin
slides/data/grid_app.json, both from one payload: the seven dials and their levels, the 2030
outcome snapshot (eleven outcomes: GDP, wages and unemployment broken out by
AI-sensitive / all-other / all-workers, plus capital, TFP, labor share and GDP
growth) for each of the 4374 combinations, and the monthly 2025-2030 paths for
the GDP gap, the AI-sensitive wage gap, and the cognitive unemployment rate.
Everything but those three charted series is snapshot-only (a table row in the
explorer, not a chart), so it has no monthly path.

Cells are stored in itertools.product order, so the JS side finds a cell by the
mixed-radix index

    index = ((level[0] * n1 + level[1]) * n2 + level[2]) ... , n_k = len(levels of dial k)

without needing a lookup key. The dials no longer all have three levels, so the radix
varies per position.
"""
import itertools, json, math, pathlib, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from aiscen.params import Fixed, Scenario, SUBSTANTIAL, gain_path
import aiscen.simulate as sim

# The paper varies each dial over three values. Reinstatement is carried at a finer grid,
# including values at and above one, where new labor tasks more than offset displacement:
# the paper's own scenarios never go there, and the region behaves qualitatively differently
# (the labor share rises rather than falls).
DIALS = [
    ("m",       "AI's reach",        "share of tasks AI can affect",                 (0.20, 0.30, 0.50)),
    ("d",       "Adoption",          "share of those instances actually done with AI",(0.20, 0.40, 0.60)),
    ("a",       "Gain",              "log cost saving per AI-performed instance",     (0.30, 0.45, 0.80)),
    ("psi",     "Automation share",  "share of AI use that replaces rather than helps",(0.50, 0.75, 0.90)),
    ("rho",     "Reinstatement",     "new labor tasks created per task automated",
     (1.25, 1.00, 0.75, 0.50, 0.25, 0.00)),
    ("mu",      "Search efficiency", "ease of moving to a new occupation",            (0.17, 0.08, 0.04)),
    ("theta_H", "Posting speed",     "share of the hiring shortfall posted per month",(0.10, 0.25, 0.50)),
]
# The three named scenarios, as a value per dial (Table 1).
NAMED = {
    "modest":      (0.20, 0.20, 0.30, 0.50, 0.50, 0.17, 0.10),
    "substantial": (0.30, 0.40, 0.45, 0.75, 0.25, 0.08, 0.25),
    "extreme":     (0.50, 0.60, 0.80, 0.90, 0.00, 0.04, 0.50),
}
# The charted monthly paths run 2025 to 2030. The model itself starts at the 2024 base
# period, but 2024 and most of 2025 are flat (the scenarios only fan out after the
# mid-2026 anchor), so the charts start in 2025 to give the curves room.
T0, T1 = 2025.0, 2030.0


def main() -> None:
    """Run every dial combination once and write the explorer's payload."""
    fixed = Fixed()
    anchor = SUBSTANTIAL.a_anchor              # 0.35, the mid-2026 gain custom paths rise from
    years = T1 - fixed.t_anchor                # 3.5 years from that anchor to 2030
    months = [T0 + k / 12.0 for k in range(int(round((T1 - T0) * 12)) + 1)]   # 61 dates

    snap, gdp_path, wage_path, u_path = [], [], [], []
    t_start = time.perf_counter()
    # itertools.product over the level INDICES of the seven dials, in DIALS order,
    # so the k-th cell written is the k-th combination in mixed-radix order (see
    # the module docstring). Each combination is one full monthly simulation.
    for combo in itertools.product(*[range(len(lv)) for _, _, _, lv in DIALS]):
        v = {k: lv[i] for (k, _, _, lv), i in zip(DIALS, combo)}      # {"m": 0.20, ...}
        a_anchor, g_a = gain_path(v["a"], anchor, years)
        res = sim.run(fixed, Scenario(
            name="grid", m_2030=v["m"], d_2030=v["d"],
            a_anchor=a_anchor, g_a=g_a,
            psi=v["psi"], rho=v["rho"], mu=v["mu"], theta_H=v["theta_H"]))
        e = res.at(T1)                          # the 2030 row
        # The 2030 snapshot: ELEVEN outcomes in a FIXED order, indexed by position.
        # The explorer's JS reads snap[cell][i] and labels it with outcomes[i] and
        # units[i] below, and tests/test_explorer_grid.py checks all three stay the
        # same length. Log gaps become percent deviations, exp(dln) - 1, as Table 3
        # reports them; shares and rates are simply times 100. Two decimals.
        snap.append([round(x, 2) for x in (
            100 * (math.exp(e.dlnY) - 1),        # GDP gap
            100 * (math.exp(e.dlnw_C_paid) - 1), # AI-sensitive wage gap (the charted wage)
            100 * (math.exp(e.dlnK) - 1),        # capital stock gap
            100 * (math.exp(e.dln_tfp) - 1),     # measured TFP gap
            100 * e.s_L,                         # labor share
            100 * e.u_rate_C,                    # cognitive unemployment
            100 * e.u_rate,                      # all-worker unemployment
            # GDP growth, pct/yr: the no-AI trend (g + n, ideas growth plus
            # labor-force growth) plus the trailing-twelve-month change in the
            # log GDP gap. Same convention aiscen/report.py's table3_column()
            # uses for the published "GDP growth, pct per year" row, reusing
            # Result.growth() rather than inventing a new discretization.
            # Snapshot-only (a table row, not a chart), so no monthly path.
            100 * (fixed.g + fixed.n + res.growth("dlnY", T1)),
            100 * (math.exp(e.dlnw_avg) - 1),    # average wage gap, all workers (table-only)
            100 * e.u_rate_N,                    # all-other-occupation unemployment (table-only)
            100 * (math.exp(e.dlnw_N) - 1),       # all-other wage gap (table-only)
        )])
        # The three charted series, monthly from 2025: same conventions as above.
        gdp_path.append([round(100 * (math.exp(res.at(t).dlnY) - 1), 2) for t in months])
        wage_path.append([round(100 * (math.exp(res.at(t).dlnw_C_paid) - 1), 2) for t in months])
        u_path.append([round(100 * res.at(t).u_rate_C, 2) for t in months])

    out = {
        "t": [round(t, 4) for t in months],
        "dials": [{"key": k, "label": lab, "desc": desc, "levels": list(lv)}
                  for k, lab, desc, lv in DIALS],
        # Display labels only: the group the paper calls "cognitive" is relabelled
        # "AI-sensitive" wherever a reader sees it, as the deck does. Keys stay.
        "outcomes": ["GDP vs no-AI", "AI-sensitive wage vs no-AI", "Capital stock vs no-AI",
                     "Measured TFP vs no-AI", "Labor share", "Unemployment, AI-sensitive",
                     "Unemployment, all workers", "GDP growth", "Average wage, all workers",
                     "Unemployment, all-other occupations", "All-other wage vs no-AI"],
        "units": ["%", "%", "%", "%", "% of income", "%", "%", "% per year", "%", "%", "%"],
        # The named scenarios as level indices per dial, so the JS can jump to them.
        "named": {name: [lv.index(v) for (_, _, _, lv), v in zip(DIALS, vals)]
                  for name, vals in NAMED.items()},
        "snap": snap, "gdp": gdp_path, "wage": wage_path, "u": u_path,
    }
    blob = json.dumps(out, separators=(",", ":"))
    p = pathlib.Path(__file__).parent / "data" / "grid_app.json"
    p.write_text(blob)
    # The explorer page loads the same payload as a script, so write it here too:
    # regenerating the JSON alone used to leave explorer/ serving a stale grid.
    js = pathlib.Path(__file__).parent.parent / "explorer" / "grid.js"
    js.write_text("window.__GRID__=" + blob + ";\n")
    shape = " x ".join(str(len(lv)) for _, _, _, lv in DIALS)
    print(f"{p}: {shape} = {len(snap)} cells, {p.stat().st_size / 1e6:.2f} MB, "
          f"{time.perf_counter() - t_start:.1f}s")
    print(f"{js}: {js.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
