"""Writes slides/data/inputs.csv: the seven scenario inputs at their 2030 values.

The monthly CSVs carry m, d, a and psi as time series, but rho, mu and theta_H are
constants within a scenario and so appear nowhere in them. The deck needs all seven
in one place, and the deck's rule is that no number is retyped, so export them here.

    python3 slides/make_inputs.py
"""

import csv
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from aiscen.params import SCENARIOS


def main() -> None:
    out = pathlib.Path(__file__).parent / "data" / "inputs.csv"
    with out.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "m", "d", "a", "psi", "rho", "mu", "theta_H"])
        for name in ("modest", "substantial", "extreme"):
            s = SCENARIOS[name]
            a_2030 = s.a_anchor + s.g_a * (2030.0 - 2026.5)
            w.writerow([name, s.m_2030, s.d_2030, round(a_2030, 6),
                        s.psi, s.rho, s.mu, s.theta_H])
    print(f"{out}: {out.stat().st_size} bytes")


if __name__ == "__main__":
    main()
