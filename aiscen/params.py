"""Parameters of Korinek, Jones, Sacher, Cotter & McCrory (2026),
"Economic Scenarios for Transformative AI", Anthropic Institute WP 2026-02.

Every number here is transcribed from Table 1 (pp. 23-25) and Table A.2
(pp. 43-45) of the working paper. Page/table references are given per field
so each value can be checked against the source.

This is an independent reimplementation; no code was released with the paper.
"""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Fixed:
    """Panel A + D of Table 1: common to all three scenarios."""

    # --- Technology and factor markets (Table 1, panel A) ---
    sigma: float = 0.5          # elasticity of substitution across task instances
    s_L0: float = 0.60          # base-period labor share
    cog_share: float = 0.624    # s_C,t0 / s_L,t0, cognitive share of employment
                                 # (CPS 2025 annual averages, https://www.bls.gov/cps/)
    eps: float = 3.0            # elasticity of capital supply
    r_bar: float = 0.115        # no-AI gross rental rate, per year
    delta: float = 0.05         # depreciation, per year

    # --- Ideas production (Table 1, panel A; Section 2.2) ---
    lam: float = 1.0            # lambda, returns to research input (no duplication)
    fishing_out_R: float = 2.86  # 1 - phi_R, labor-augmenting units, research in goods
    g: float = 0.0167           # no-AI growth of the ideas stock, per year
    n: float = 0.0033           # labor-force growth, per year
    iota_R0: float = 0.035      # research share of GDP in 2024
    g_iota: float = 0.028       # growth of the research share, per year

    # --- Dates (Table 1, panel A) ---
    t0: float = 2024.0          # base period
    t_anchor: float = 2026.5    # mid-2026, where the AI paths are anchored
    t_target: float = 2030.0    # date of the scenarios' 2030 values

    # --- The labor market in normal times (Table 1, panel D) ---
    q_bar_ann: float = 0.11     # normal quit rate, per year
    q_resp_share: float = 0.55  # q^T_o / q_bar_o, share of quits responding to prospects
    q_rel_C: float = 0.69       # q_bar_C / q_bar
    q_rel_N: float = 1.52       # q_bar_N / q_bar
    U_bar: float = 0.038        # normal search pool, share of the labor force
    mu_bar: float = 0.17        # search discount in normal times
    iota_match: float = 1.27    # matching curvature (den Haan et al. 2000)
    fill_bar: float = 0.65      # employment-weighted mean monthly filling rate
    # Table 1 lists wage rigidity in panel C, with the disruptiveness inputs; it sits
    # here with the other labor-market parameters because that is how the code uses it.
    xi: float = 0.50            # rigidity of the cognitive wage, per year (Table 1, panel C)

    # --- Numerical / convention switches (Appendix A, p. 40) ---
    h: float = 1.0 / 12.0       # period length, one month
    cc_rates: bool = True       # "a quit fraction q enters as -ln(1-q)"

    # --- Derived ---
    @property
    def s_K0(self) -> float:
        return 1.0 - self.s_L0

    @property
    def s_C0(self) -> float:
        return self.s_L0 * self.cog_share

    @property
    def s_N0(self) -> float:
        return self.s_L0 * (1.0 - self.cog_share)

    @property
    def phi_R(self) -> float:
        return 1.0 - self.fishing_out_R

    @property
    def L(self) -> float:
        """Labor force, in units where head counts are shares of it."""
        return 1.0

    @property
    def L_emp0(self) -> float:
        """L - U_bar: base-period employment."""
        return self.L - self.U_bar

    @property
    def l_C0(self) -> float:
        return self.cog_share * self.L_emp0

    @property
    def l_N0(self) -> float:
        return (1.0 - self.cog_share) * self.L_emp0

    def rate(self, x: float) -> float:
        """Convert a per-period fraction to the model's rate (Appendix A, p. 40)."""
        import math
        return -math.log(1.0 - x) if self.cc_rates else x

    @property
    def q_bar_C(self) -> float:
        return self.rate(self.q_bar_ann / 12.0 * self.q_rel_C)

    @property
    def q_bar_N(self) -> float:
        return self.rate(self.q_bar_ann / 12.0 * self.q_rel_N)


@dataclass(frozen=True)
class Scenario:
    """Panels B and C of Table 1: one column of the scenario table."""

    name: str
    # AI in production (Table 1, panel B)
    m_anchor: float = 0.14      # affected mass, mid-2026 (common to scenarios)
    m_2030: float = 0.30
    d_anchor: float = 0.10      # diffusion share, mid-2026 (common)
    d_2030: float = 0.40
    a_anchor: float = 0.35      # log gain per instance, mid-2026
    g_a: float = 0.028          # slope of the gain, per year
    d_ceiling: float = 1.0      # d_bar
    # Disruptiveness (Table 1, panel C)
    psi: float = 0.75           # automation share, held constant
    rho: float = 0.25           # reinstatement ratio
    mu: float = 0.08            # search discount on the path
    theta_H: float = 0.25       # posting speed, per month


MODEST = Scenario(
    name="modest", m_2030=0.20, d_2030=0.20, a_anchor=0.30, g_a=0.0,
    psi=0.50, rho=0.50, mu=0.17, theta_H=0.10,
)
SUBSTANTIAL = Scenario(
    name="substantial", m_2030=0.30, d_2030=0.40, a_anchor=0.35, g_a=0.028,
    psi=0.75, rho=0.25, mu=0.08, theta_H=0.25,
)
EXTREME = Scenario(
    name="extreme", m_2030=0.50, d_2030=0.60, a_anchor=0.45, g_a=0.10,
    psi=0.90, rho=0.00, mu=0.04, theta_H=0.50,
)

SCENARIOS = {s.name: s for s in (MODEST, SUBSTANTIAL, EXTREME)}


def scenario_from_2030_values(name: str, m_2030: float, d_2030: float, a_2030: float,
                              psi: float, mu: float, base: Scenario = SUBSTANTIAL,
                              t_anchor: float = 2026.5, t_target: float = 2030.0) -> Scenario:
    """Build a scenario from 2030 values, as the scenario explorer does for a user's
    (or a survey respondent's) answers.

    The mid-2026 anchors for m and d are common to all scenarios (0.14 and 0.10).
    The gain a_t is linear from its anchor to the chosen 2030 value; the anchor is
    taken from `base`, since the paper does not say which anchor a survey run uses.
    Everything not asked about in the survey stays at `base` (Table 4 note:
    rho = 0.25, theta_H = 0.25, xi = 0.5, eps = 3).
    """
    years = t_target - t_anchor
    return Scenario(
        name=name,
        m_anchor=base.m_anchor, m_2030=m_2030,
        d_anchor=base.d_anchor, d_2030=d_2030,
        a_anchor=base.a_anchor, g_a=(a_2030 - base.a_anchor) / years,
        psi=psi, rho=base.rho, mu=mu, theta_H=base.theta_H,
    )


# Table 2 (p. 30): the medians of the five parameters implied by the survey of
# 10,980 US adults (Morning Consult, 11-23 August 2026). Table 4's columns are
# medians of outcomes across respondents, not the outcome at the median answers,
# so running this scenario is indicative rather than a replication of Table 4.
SURVEY_MEDIAN = scenario_from_2030_values(
    "survey_median", m_2030=0.44, d_2030=0.40, a_2030=0.44, psi=0.47, mu=0.064,
)
