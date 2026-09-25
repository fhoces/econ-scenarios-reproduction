"""Run the full 3^7 factorial over the seven scenario dials and export it for the deck.

The three named scenarios are one diagonal through this grid: each dial is set to its
modest / substantial / extreme value simultaneously. Here every combination is run.

    python3 slides/make_grid.py     ->  slides/data/grid.csv   (2187 rows)
"""
import csv, itertools, math, pathlib, sys, time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from aiscen.params import Fixed, Scenario, SUBSTANTIAL, gain_path
import aiscen.simulate as sim

# Each dial's three levels, in the order modest / substantial / extreme (Table 1).
LEVELS = {
    "m": (0.20, 0.30, 0.50),
    "d": (0.20, 0.40, 0.60),
    "a": (0.30, 0.45, 0.80),
    "psi": (0.50, 0.75, 0.90),
    "rho": (0.50, 0.25, 0.00),
    "mu": (0.17, 0.08, 0.04),
    "theta_H": (0.10, 0.25, 0.50),
}
NAMES = ("modest", "substantial", "extreme")


def main() -> None:
    """Run all 3^7 combinations and write one row each: the seven inputs, their
    level sum (0 = all modest, 14 = all extreme, the deck's x-axis), and three
    2030 outcomes in percent."""
    fixed = Fixed()
    anchor = SUBSTANTIAL.a_anchor          # custom gains above it rise from this 2026 anchor
    years = 2030.0 - fixed.t_anchor        # 3.5
    out = pathlib.Path(__file__).parent / "data" / "grid.csv"

    t0 = time.perf_counter()
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(list(LEVELS) + ["level_sum", "gdp", "u_C", "s_L"])
        for combo in itertools.product(*[range(3) for _ in LEVELS]):
            v = {k: LEVELS[k][i] for k, i in zip(LEVELS, combo)}
            a_anchor, g_a = gain_path(v["a"], anchor, years)
            scen = Scenario(
                name="grid", m_2030=v["m"], d_2030=v["d"],
                a_anchor=a_anchor, g_a=g_a,
                psi=v["psi"], rho=v["rho"], mu=v["mu"], theta_H=v["theta_H"],
            )
            m = sim.run(fixed, scen).at(2030.0)
            w.writerow(list(v.values()) + [sum(combo),
                                           100 * (math.exp(m.dlnY) - 1),
                                           100 * m.u_rate_C, 100 * m.s_L])
    print(f"{out}: 3^{len(LEVELS)} = {3 ** len(LEVELS)} cells "
          f"in {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
