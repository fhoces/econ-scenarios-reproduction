#!/usr/bin/env python3
"""Reproduce the paper's tables and write the simulated monthly paths to CSV.

    python3 run.py               # print Table 3, 5, 6 comparisons
    python3 run.py --csv out/    # also write per-scenario monthly paths and the
                                 # table3/table5/table6/slop comparison CSVs
"""

import argparse
import csv
import math
import os
from dataclasses import asdict, fields

from aiscen import simulate
from aiscen.params import Fixed, SCENARIOS, SURVEY_MEDIAN
from aiscen.report import (PUBLISHED, ROW_ORDER, TABLE5, TABLE5_ROWS, TABLE6,
                           TABLE6_ROWS, build_table3, compare, table3_column)


def robustness_table(title, spec, rows, field_name):
    out = [f"\n{title}"]
    head = f"{'Row':44s}" + "".join(f"{'sim/pub':>16s}" for _ in range(len(spec) // 2))
    for scen in ("substantial", "extreme"):
        keys = [k for k in spec if k[0] == scen]
        cols = {}
        for k in keys:
            kw = {field_name: k[1]}
            f = Fixed(**kw)
            cols[k] = table3_column(simulate.run(f, SCENARIOS[scen]))
        out.append(f"  {scen}:  " + "  ".join(f"{field_name}={k[1]}" for k in keys))
        for i, row in enumerate(rows):
            cells = []
            for k in keys:
                cells.append(f"{cols[k][row]:7.2f}/{spec[k][i]:6.1f}")
            out.append(f"    {row:42s}" + "".join(f"{c:>16s}" for c in cells))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", metavar="DIR", help="write monthly paths to DIR")
    ap.add_argument("--survey", action="store_true", help="also run the survey-median scenario")
    args = ap.parse_args()

    print("Table 3: the three scenarios in 2030 (paper p. 31)")
    print(compare())
    print(robustness_table("Table 5: elasticities of capital supply (paper p. 37)",
                           TABLE5, TABLE5_ROWS, "eps"))
    print(robustness_table("Table 6: rigidities of the cognitive wage (paper p. 38)",
                           TABLE6, TABLE6_ROWS, "xi"))

    if args.survey:
        col = table3_column(simulate.run(Fixed(), SURVEY_MEDIAN))
        print("\nSurvey-median parameters (Table 2), indicative only: Table 4 reports")
        print("medians of outcomes across respondents, not outcomes at median answers.")
        for k in ("GDP, pct above no-AI", "GDP growth, pct per year",
                  "Average wage, pct above no-AI", "  cognitive occupations w_C",
                  "  all other occupations w_N", "Labor share, pct of income",
                  "Cognitive employment, pct since mid-2026",
                  "Unemployment rate, cognitive, pct", "Unemployment rate, all workers, pct"):
            print(f"    {k:44s} {col[k]:8.2f}")

    if args.csv:
        os.makedirs(args.csv, exist_ok=True)
        # The published-comparison tables, so downstream consumers (the slide deck)
        # read the model's own output rather than transcribing numbers by hand.
        for name, spec, rows_ in (("table5", TABLE5, TABLE5_ROWS),
                                  ("table6", TABLE6, TABLE6_ROWS)):
            field = "eps" if name == "table5" else "xi"
            path = os.path.join(args.csv, f"{name}.csv")
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(["scenario", field, "row", "simulated", "published"])
                for (scen, val), want in spec.items():
                    kw = {field: val}
                    col = table3_column(simulate.run(Fixed(**kw), SCENARIOS[scen]))
                    for r, pub in zip(rows_, want):
                        w.writerow([scen, val, r, f"{col[r]:.4f}", pub])
            print(f"wrote {path}")
        # the slop extension, for the deck
        from aiscen import slop
        path = os.path.join(args.csv, "slop.csv")
        # report.py indents some row labels for the printed table; strip that here so
        # the CSV header round-trips through readers that trim leading whitespace.
        slop_rows = [{k.strip(): v for k, v in row.items()} for row in slop.cases(Fixed())]
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(slop_rows[0]))
            w.writeheader()
            w.writerows(slop_rows)
        print(f"wrote {path} (critical gain "
              f"{slop.critical_gain(Fixed()):.3f})")

        path = os.path.join(args.csv, "table3.csv")
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["row", "no_ai", "modest", "substantial", "extreme",
                        "pub_no_ai", "pub_modest", "pub_substantial", "pub_extreme"])
            t3 = build_table3(Fixed())
            for row in ROW_ORDER:
                w.writerow([row] + [f"{x:.4f}" for x in t3[row]] + list(PUBLISHED[row]))
        print(f"wrote {path}")
        names = list(SCENARIOS) + (["survey_median"] if args.survey else [])
        for name in names:
            scen = SURVEY_MEDIAN if name == "survey_median" else SCENARIOS[name]
            res = simulate.run(Fixed(), scen)
            path = os.path.join(args.csv, f"{name}.csv")
            cols = [f.name for f in fields(simulate.Month)]
            with open(path, "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols)
                w.writeheader()
                for row in res.months:
                    w.writerow(asdict(row))
            print(f"wrote {path} ({len(res.months)} months x {len(cols)} columns)")


if __name__ == "__main__":
    main()
