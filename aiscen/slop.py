"""An extension the paper does not run: what "AI slop" looks like in this model.

Slop means AI output that is plausible but low quality, so that using it costs time
in checking and rework. That is not outside the model: the paper's gain per instance
a_t is defined all-in, net of checking (the survey asks for time "counting the time
spent checking and fixing the AI's work"), so slop is the claim that the realised a_t
is far below the 0.30-0.45 taken from field trials.

The asymmetry that makes it consequential is visible in the labor-share row of
Equation (11): displacement, (1 - rho) psi m d, does not contain a, while the weak-link
term that protects the labor share, (1 - sigma) psi m d a, is proportional to it. (The
same displacement term leads Equation (19).) Slop removes the offset
and leaves the harm.

Nothing here is in the paper; it is a sensitivity analysis its equations support.
"""

from dataclasses import replace

from .numerics import bisect
from .params import Fixed, SCENARIOS, Scenario
from .paths import Paths
from .report import table3_column
from .simulate import run

# The extension runs off the substantial scenario, and reports the seven Table 3 rows
# the deck's slop table shows (in table3_column's row names).
BASE = SCENARIOS["substantial"]
REPORT_ROWS = [
    "GDP, pct above no-AI",
    "Measured TFP, pct above no-AI",
    "Average wage, pct above no-AI",
    "  cognitive occupations w_C",
    "Labor share, pct of income",
    "Cognitive employment, pct since mid-2026",
    "Unemployment rate, cognitive, pct",
]


def gain_2030(scen: Scenario, years: float = 3.5) -> float:
    """The scenario's 2030 all-in gain per AI-performed instance."""
    return scen.a_anchor + scen.g_a * years


def scale_gain(scen: Scenario, a_2030: float, name: str = None) -> Scenario:
    """Rescale the whole a-path so it lands on `a_2030`, keeping its shape.

    Both the mid-2026 anchor and the slope are multiplied by the same factor, so a
    slop world is one where the gain was always lower, not one where it collapses
    suddenly in 2030.
    """
    k = a_2030 / gain_2030(scen)
    return replace(scen, name=name or f"a={a_2030:.2f}",
                   a_anchor=scen.a_anchor * k, g_a=scen.g_a * k)


def eps_star(f: Fixed, scen: Scenario, t: float = 2030.0) -> float:
    """Equation (12): the capital-supply elasticity above which the wage rises."""
    x = Paths.build(f, scen).at(t)
    if x["a"] < 1e-3:
        # (1 - rho)/a diverges: with no cost saving at all, no finite elasticity of
        # capital supply lets the average wage rise.
        return float("inf")
    return (f.s_K0 - f.sigma
            + x["psi"] * ((1.0 - x["rho"]) / x["a"] - (1.0 - f.sigma))) / f.s_L0


def decomposition(f: Fixed, scen: Scenario, t: float = 2030.0) -> dict:
    """The labor-share row of Equation (11), and the employment target (19), split into
    the parts that scale with a and the part that does not."""
    x = Paths.build(f, scen).at(t)
    displacement = (1.0 - x["rho"]) * x["psi"] * x["md"]
    cushion = (1.0 - f.sigma) * (1.0 - x["psi"]) * x["md"] * x["a"]
    share_cushion = (1.0 - f.sigma) * x["psi"] * x["md"] * x["a"]   # the labor-share term
    return {"a_2030": x["a"], "displacement": displacement,
            "labor released by gains": cushion, "weak-link cushion": share_cushion,
            "ratio": displacement / share_cushion if share_cushion else float("inf")}


def cases(f: Fixed = None, base: Scenario = BASE) -> list:
    """The slop variants, each one or two field changes to the substantial scenario."""
    f = f or Fixed()
    a0 = gain_2030(base)
    variants = [
        ("substantial (baseline)", base),
        ("all-in gain halved", scale_gain(base, a0 / 2, "slop-half")),
        ("gain halved, checking becomes new human work",
         replace(scale_gain(base, a0 / 2), name="slop-rho", rho=0.50)),
        ("gain halved, adoption stalls",
         replace(scale_gain(base, a0 / 2), name="slop-diffusion", d_2030=0.25)),
        ("all-in gain quartered", scale_gain(base, a0 / 4, "slop-quarter")),
        ("pure slop: no time saved at all", scale_gain(base, 1e-6, "slop-zero")),
    ]
    out = []
    for label, scen in variants:
        col = table3_column(run(f, scen))
        row = {"case": label, "a_2030": gain_2030(scen), "eps_star": eps_star(f, scen)}
        row.update({r: col[r] for r in REPORT_ROWS})
        out.append(row)
    return out


def critical_gain(f: Fixed = None, base: Scenario = BASE, lo: float = 0.02,
                  hi: float = None) -> float:
    """The all-in gain at which the average wage stops rising.

    Below this, AI in the substantial scenario leaves the average worker worse off
    than no AI at all, at the paper's calibrated capital-supply elasticity.
    """
    f = f or Fixed()
    hi = hi or gain_2030(base)
    # Bracket for the bisection. The low end starts a little above zero rather than
    # at zero: the wage is already negative there (the pure-slop case at a = 1e-6
    # gives about -3 percent, tests/test_robustness.py), so nothing is lost, and it
    # keeps the search away from the corner where the (1 - rho)/a term of eps_star
    # diverges. The high end is the scenario's own 2030 gain, where the wage is
    # positive, so the sign change lies inside.

    def wage(a):
        return table3_column(run(f, scale_gain(base, a)))["Average wage, pct above no-AI"]

    return bisect(wage, lo, hi, tol=1e-4, maxiter=40)
