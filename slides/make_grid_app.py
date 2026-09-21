"""Export every cell of the 3^7 dial grid, with paths, for the static explorer page.

Writes slides/data/grid_app.json: the seven dials and their three levels, the 2030
outcome snapshot for each of the 2187 combinations, and the monthly 2025-2030 paths
for the GDP gap and the cognitive unemployment rate.

Cells are stored in itertools.product order, so the JS side finds a cell by the
mixed-radix index

    index = ((level[0] * n1 + level[1]) * n2 + level[2]) ... , n_k = len(levels of dial k)

without needing a lookup key. The dials no longer all have three levels, so the radix
varies per position.
"""
import itertools, json, math, pathlib, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from aiscen.params import Fixed, Scenario, SUBSTANTIAL
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
T0, T1 = 2025.0, 2030.0


def main() -> None:
    fixed = Fixed()
    anchor = SUBSTANTIAL.a_anchor
    years = T1 - fixed.t_anchor
    months = [T0 + k / 12.0 for k in range(int(round((T1 - T0) * 12)) + 1)]

    snap, gdp_path, u_path = [], [], []
    t_start = time.perf_counter()
    for combo in itertools.product(*[range(len(lv)) for _, _, _, lv in DIALS]):
        v = {k: lv[i] for (k, _, _, lv), i in zip(DIALS, combo)}
        res = sim.run(fixed, Scenario(
            name="grid", m_2030=v["m"], d_2030=v["d"],
            a_anchor=anchor, g_a=(v["a"] - anchor) / years,
            psi=v["psi"], rho=v["rho"], mu=v["mu"], theta_H=v["theta_H"]))
        e = res.at(T1)
        snap.append([round(x, 2) for x in (
            100 * (math.exp(e.dlnY) - 1),        # GDP gap
            100 * (math.exp(e.dlnw_avg) - 1),    # average wage gap
            100 * (math.exp(e.dlnK) - 1),        # capital stock gap
            100 * (math.exp(e.dln_tfp) - 1),     # measured TFP gap
            100 * e.s_L,                         # labor share
            100 * e.u_rate_C,                    # cognitive unemployment
            100 * e.u_rate,                      # all-worker unemployment
        )])
        gdp_path.append([round(100 * (math.exp(res.at(t).dlnY) - 1), 2) for t in months])
        u_path.append([round(100 * res.at(t).u_rate_C, 2) for t in months])

    out = {
        "t": [round(t, 4) for t in months],
        "dials": [{"key": k, "label": lab, "desc": desc, "levels": list(lv)}
                  for k, lab, desc, lv in DIALS],
        "outcomes": ["GDP vs no-AI", "Average wage vs no-AI", "Capital stock vs no-AI",
                     "Measured TFP vs no-AI", "Labor share", "Unemployment, cognitive",
                     "Unemployment, all workers"],
        "units": ["%", "%", "%", "%", "% of income", "%", "%"],
        "named": {name: [lv.index(v) for (_, _, _, lv), v in zip(DIALS, vals)]
                  for name, vals in NAMED.items()},
        "snap": snap, "gdp": gdp_path, "u": u_path,
    }
    p = pathlib.Path(__file__).parent / "data" / "grid_app.json"
    p.write_text(json.dumps(out, separators=(",", ":")))
    shape = " x ".join(str(len(lv)) for _, _, _, lv in DIALS)
    print(f"{p}: {shape} = {len(snap)} cells, {p.stat().st_size / 1e6:.2f} MB, "
          f"{time.perf_counter() - t_start:.1f}s")


if __name__ == "__main__":
    main()
