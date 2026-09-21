"""Export the 44 equations of Table A.1, evaluated at month 0, for the deck.

Month 0 is t0 = 2024.0, the base period. Nothing is zero: the logistics for m and d
are already slightly above zero in 2024, so every row carries a small live value, which
is what makes the month a useful worked example rather than a table of zeros.

    python3 slides/make_month0.py  ->  slides/data/month0.csv
"""
import csv, math, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from aiscen.params import Fixed, SUBSTANTIAL
import aiscen.simulate as sim

SCEN = SUBSTANTIAL


def main() -> None:
    f = Fixed()
    res = sim.run(f, SCEN)
    r = res.months[0]
    ss = res.ss
    assert abs(r.t - f.t0) < 1e-9, r.t

    # Panel B's capital row is the frictionless one; the CSV carries only the actual,
    # so rebuild it from the starred values by Equation (17).
    dlnK_star = (math.log((1.0 - r.s_L_star) / f.s_K0) + r.dlnYL_star - r.dlnr_star)

    rows = [
        # panel, eq, variable, what it is, value
        ("A", "22", "Δln R", "research uplift = the GDP gap", r.dlnR),
        ("A", "42", "Δg", "growth gap of the ideas stock", r.dg),
        ("A", "43", "Δln A", "ideas stock, carried into t+1", r.dlnA),

        ("B", "18, 6", "Δln r*", "rental gap clearing the capital market", r.dlnr_star),
        ("B", "15", "ℓ̃_N", "shift in demand for all-other labor", r.ell_N_tilde),
        ("B", "14", "s_L*", "labor share at the targets", r.s_L_star),
        ("B", "16", "Δln w*", "common wage", r.dlnw_common),
        ("B", "5", "Δln(Y/L)*", "output per worker", r.dlnYL_star),
        ("B", "17", "Δln K*", "capital at the targets", dlnK_star),
        ("B", "45", "Δln TFP", "measured TFP", r.dln_tfp),
        ("B", "13", "ℓ*_N", "employment target, all other", r.l_N_star),
        ("B", "13", "ℓ*_C", "employment target, AI-sensitive", r.l_C_star),

        ("C", "28", "G_C", "overhang, AI-sensitive", r.G_C),
        ("C", "28", "G_N", "overhang, all other (zero on these paths)", 0.0),
        ("C", "28", "B_C", "shortfall, AI-sensitive (negligible)", 0.0),
        ("C", "28", "B_N", "shortfall, all other", r.B_N),
        ("C", "27", "q_C", "quit rate, AI-sensitive", r.q_C),
        ("C", "27", "q_N", "quit rate, all other", r.q_N),
        ("C", "29", "N_C", "attached AI-sensitive force", r.N_C),
        ("C", "30", "ln(w_C/w)", "sticky AI-sensitive wage, relative", r.x_C),
        ("C", "39", "ℓ^d_C", "AI-sensitive labor demand at that wage", r.l_C_demand),
        ("C", "31", "D_C", "layoffs, AI-sensitive", r.D_C),
        ("C", "31", "D_N", "layoffs, all other (zero by construction)", 0.0),
        ("C", "32", "v_C", "openings, AI-sensitive", r.v_C),
        ("C", "32", "v_N", "openings, all other", r.v_N),
        ("C", "33", "S_C", "effective search, AI-sensitive", r.S_C),
        ("C", "33", "S_N", "effective search, all other", r.S_N),
        ("C", "34", "H_C", "hires, AI-sensitive", r.H_C),
        ("C", "34", "H_N", "hires, all other", r.H_N),
        ("C", "35", "f_C", "finding rate, AI-sensitive origin", r.f_C),
        ("C", "35", "f_N", "finding rate, all-other origin", r.f_N),
        ("C", "36", "ℓ_C,t+1", "employment next month, AI-sensitive", res.months[1].l_C),
        ("C", "36", "ℓ_N,t+1", "employment next month, all other", res.months[1].l_N),
        ("C", "37", "U_C,t+1", "pool next month, AI-sensitive", res.months[1].U_C),
        ("C", "37", "U_N,t+1", "pool next month, all other", res.months[1].U_N),

        ("D", "19", "ℓ̃_C", "AI-sensitive shift", r.cog_shift),
        ("D", "—", "u^x", "pool above its normal level", r.u_excess),
        ("D", "39", "Δln Y", "actual GDP", r.dlnY),
        ("D", "39", "Δln w_N", "actual all-other wage", r.dlnw_N),
        ("D", "39", "Δln r", "actual rental rate", r.dlnr),
        ("D", "39", "Δln K", "actual capital stock", r.dlnK),
        ("D", "39", "s_L", "actual labor share", r.s_L),
        ("D", "—", "X", "reallocation flow", r.reallocation),
        ("D", "—", "G", "aggregate overhang", r.overhang),
    ]
    assert len(rows) == 44, len(rows)

    out = pathlib.Path(__file__).parent / "data" / "month0.csv"
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["panel", "eq", "variable", "what", "value"])
        for panel, eq, var, what, val in rows:
            w.writerow([panel, eq, var, what, f"{val:.6g}"])
    counts = {p: sum(1 for x in rows if x[0] == p) for p in "ABCD"}
    print(f"{out}: {len(rows)} equations at t = {r.t}, scenario {SCEN.name}; per panel {counts}")


if __name__ == "__main__":
    main()
